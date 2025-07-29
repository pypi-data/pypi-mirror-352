"""
TimeSHAP Explainer (pruning-enhanced SHAP for sequential models).

## Theoretical Explanation

TimeSHAP is a SHAP-style feature attribution method for sequential or event-based models that uses pruning to efficiently estimate attributions over time-event windows. It implements KernelSHAP-style estimation, but avoids the combinatorial explosion of possible feature/time subsets by pruning to the most important events or windows. TimeSHAP supports attribution at the timestep, feature, or event (window) level.

### Key Concepts

- **Pruned Coalition Sampling:** Instead of exhaustively sampling all possible coalitions, TimeSHAP first estimates rough importances for all units (timesteps, features, or events), then prunes to the top-k most important units for refined estimation.
- **Event/Window Support:** Attributions can be computed for individual timesteps, features, or over sliding windows of events.
- **Flexible Masking:** Masked features can be imputed with zeros or mean values from the background data.
- **Additivity Normalization:** Attributions are normalized so their sum matches the model output difference between the original and fully-masked input.

## Algorithm

1. **Initialization:**
    - Accepts a model, background data, masking strategy, event window size, pruning parameter, and device.
2. **Rough Importance Estimation:**
    - For each unit (timestep, feature, or event window), estimate its marginal contribution by sampling random coalitions and measuring the change in model output.
3. **Pruning:**
    - If pruning is enabled, select the top-k most important units for further analysis.
4. **Refined Attribution:**
    - For each selected unit, sample random coalitions and compute the marginal contribution more accurately.
    - Assign attributions to the appropriate timesteps, features, or events.
5. **Normalization:**
    - Scale attributions so their sum matches the difference between the original and fully-masked model output.
"""

import numpy as np
import torch
import random
from shap_enhanced.base_explainer import BaseExplainer

class TimeSHAPExplainer(BaseExplainer):
    """
    TimeSHAP: SHAP with pruning for sequential/event models, supporting true per-(t, f) attributions.

    Parameters
    ----------
    model : Any
        The model to be explained.
    background : np.ndarray or torch.Tensor
        Background data for imputation (N, T, F).
    mask_strategy : str
        'zero' or 'mean' (default).
    event_window : int or None
        If set, computes SHAP over windows of this size instead of single (t, f) units.
    prune_topk : int or None
        If set, after initial run, prune to top-k most important units, then resample only these.
    device : str
        'cpu' or 'cuda'.
    """
    def __init__(
        self, model, background,
        mask_strategy="mean",
        event_window=None,
        prune_topk=None,
        device=None
    ):
        super().__init__(model, background)
        self.mask_strategy = mask_strategy
        self.event_window = event_window
        self.prune_topk = prune_topk
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        if mask_strategy == "mean":
            self._mean = background.mean(axis=0)
        else:
            self._mean = None

    def _impute(self, X, mask_idxs):
        X_imp = X.copy()
        for (t, f) in mask_idxs:
            if self.mask_strategy == "zero":
                X_imp[t, f] = 0.0
            elif self.mask_strategy == "mean":
                X_imp[t, f] = self._mean[t, f]
            else:
                raise ValueError(f"Unknown mask_strategy: {self.mask_strategy}")
        return X_imp

    def _get_mask_idxs(self, T, F, idx, window=None):
        if window is None:
            # idx = (t, f)
            return [idx]
        # For event/window-level, mask all (t, f) within the window centered at t
        t0 = max(0, idx - window // 2)
        t1 = min(T, idx + window // 2 + 1)
        return [(t, f) for t in range(t0, t1) for f in range(F)]

    def shap_values(
        self, X,
        nsamples=100,
        level="timestep",  # or 'feature' or 'event'
        check_additivity=True,
        random_seed=42,
        **kwargs
    ):
        """
        Computes SHAP attributions at timestep-feature, event, or feature level using pruned coalition sampling.
        """
        np.random.seed(random_seed)
        random.seed(random_seed)
        is_torch = hasattr(X, 'detach')
        X_in = X.detach().cpu().numpy() if is_torch else np.asarray(X)
        if len(X_in.shape) == 2:
            X_in = X_in[None, ...]
            single = True
        else:
            single = False
        B, T, F = X_in.shape

        # Build units for masking
        if self.event_window is not None and level == "event":
            # Each unit is a window of timesteps
            units = list(range(T - self.event_window + 1))
            mask_unit = lambda u: self._get_mask_idxs(T, F, u, window=self.event_window)
        elif level == "timestep":
            # Each unit is a (t, f) pair
            units = [(t, f) for t in range(T) for f in range(F)]
            mask_unit = lambda u: [u]
        elif level == "feature":
            # Each unit is a feature index
            units = list(range(F))
            mask_unit = lambda u: [(t, u) for t in range(T)]
        else:
            raise ValueError(f"Unknown level {level}")

        shap_vals = np.zeros((B, T, F), dtype=float)

        for b in range(B):
            x_orig = X_in[b]

            # === First pass: rough importance for all units ===
            approx_contribs = []
            for idx in units:
                contribs = []
                for _ in range(nsamples):
                    unit_candidates = [u for u in units if u != idx]
                    if len(unit_candidates) == 0:
                        C = []
                    else:
                        k = np.random.randint(1, len(unit_candidates)+1)
                        C = random.sample(unit_candidates, k) if len(unit_candidates) >= k else unit_candidates
                    # Build mask indices from coalition
                    mask_idxs = []
                    for u in C:
                        mask_idxs.extend(mask_unit(u))
                    x_S = self._impute(x_orig, mask_idxs)
                    # Mask union: coalition + current idx
                    mask_idxs_union = mask_idxs + mask_unit(idx)
                    x_S_union = self._impute(x_orig, mask_idxs_union)
                    out_S = self.model(torch.tensor(x_S[None], dtype=torch.float32, device=self.device)).detach().cpu().numpy().squeeze()
                    out_S_union = self.model(torch.tensor(x_S_union[None], dtype=torch.float32, device=self.device)).detach().cpu().numpy().squeeze()
                    contribs.append(out_S - out_S_union)
                approx_contribs.append(np.mean(contribs))

            # === Prune to top-k units if enabled ===
            active_units = units
            if self.prune_topk is not None and self.prune_topk < len(units):
                topk_units_idx = np.argsort(np.abs(approx_contribs))[-self.prune_topk:]
                active_units = [units[i] for i in topk_units_idx]

            # === Second pass: refined estimation on pruned set ===
            for idx in active_units:
                contribs = []
                unit_candidates = [u for u in active_units if u != idx]
                for _ in range(nsamples):
                    if len(unit_candidates) == 0:
                        C = []
                    else:
                        k = np.random.randint(1, len(unit_candidates)+1)
                        C = random.sample(unit_candidates, k) if len(unit_candidates) >= k else unit_candidates
                    mask_idxs = []
                    for u in C:
                        mask_idxs.extend(mask_unit(u))
                    x_S = self._impute(x_orig, mask_idxs)
                    mask_idxs_union = mask_idxs + mask_unit(idx)
                    x_S_union = self._impute(x_orig, mask_idxs_union)
                    out_S = self.model(torch.tensor(x_S[None], dtype=torch.float32, device=self.device)).detach().cpu().numpy().squeeze()
                    out_S_union = self.model(torch.tensor(x_S_union[None], dtype=torch.float32, device=self.device)).detach().cpu().numpy().squeeze()
                    contribs.append(out_S - out_S_union)

                # Assign to output
                if self.event_window is not None and level == "event":
                    for t, f in mask_unit(idx):
                        shap_vals[b, t, f] += np.mean(contribs) / self.event_window  # distribute over window
                elif level == "timestep":
                    t, f = idx
                    shap_vals[b, t, f] = np.mean(contribs)
                elif level == "feature":
                    for t in range(T):
                        shap_vals[b, t, idx] = np.mean(contribs)

            # === Normalization for additivity ===
            all_pos = [(t, f) for t in range(T) for f in range(F)]
            orig_pred = self.model(torch.tensor(x_orig[None], dtype=torch.float32, device=self.device)).detach().cpu().numpy().squeeze()
            x_all_masked = self._impute(x_orig, all_pos)
            masked_pred = self.model(torch.tensor(x_all_masked[None], dtype=torch.float32, device=self.device)).detach().cpu().numpy().squeeze()
            shap_sum = shap_vals[b].sum()
            model_diff = orig_pred - masked_pred
            if shap_sum != 0:
                shap_vals[b] *= model_diff / shap_sum

        shap_vals = shap_vals[0] if single else shap_vals
        if check_additivity:
            print(f"[TimeSHAP Additivity] sum(SHAP)={shap_vals.sum():.4f} | Model diff={float(orig_pred - masked_pred):.4f}")
        return shap_vals
