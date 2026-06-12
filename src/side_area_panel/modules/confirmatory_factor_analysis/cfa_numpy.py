#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2


class CFAResultStruct:
    def __init__(self, loadings, phi, uniq, fit_indices, converged, message, std_loadings=None, std_resid=None):
        self.loadings_ = loadings
        self.phi_ = phi
        self.uniq_ = uniq
        self.fit_indices_ = fit_indices
        self.converged_ = converged
        self.message_ = message
        self.std_loadings_ = std_loadings
        self.std_resid_ = std_resid


class CFAEstimator:
    """
    Confirmatory Factor Analysis (CFA) estimator using maximum likelihood.
    structure: list of lists of variable names (per factor)
    allow_factor_correlation: if True, estimate factor correlations (oblique), else orthogonal
    fixed_loadings: optional, dict {(var, factor): value} to fix certain loadings (not wired to UI)
    """

    def __init__(self, structure, allow_factor_correlation=True, max_iter=200, tol=1e-6, fixed_loadings=None):
        self.structure = structure
        self.allow_factor_correlation = allow_factor_correlation
        self.max_iter = max_iter
        self.tol = tol
        self.fixed_loadings = fixed_loadings if fixed_loadings is not None else {}

    def fit(self, X, var_names=None):
        """
        Fit the CFA model to data X. Only listwise deletion is supported for missing data.
        Parameters:
            X: np.ndarray, shape (n_samples, n_variables)
            var_names: list of str, optional
        Returns:
            CFAResultStruct
        """
        # Listwise deletion for missing data
        if np.isnan(X).any():
            X = X[~np.isnan(X).any(axis=1)]
        n_obs, n_vars = X.shape
        # Standardize, so the model is fit on the correlation matrix. Factor variances are
        # fixed to 1, so this is the natural scale; it is far better-conditioned than the raw
        # covariance, which (with free factor correlations) let the optimiser push Phi to the
        # +/-1 boundary (a singular, degenerate solution).
        col_std = X.std(axis=0, ddof=0)
        col_std[col_std == 0] = 1.0
        X = (X - X.mean(axis=0)) / col_std
        n_factors = len(self.structure)
        if var_names is None:
            var_names = [f"x{i+1}" for i in range(n_vars)]
        # Build loading mask
        mask = np.zeros((n_vars, n_factors), dtype=bool)
        for j, factor_vars in enumerate(self.structure):
            for v in factor_vars:
                if v in var_names:
                    i = var_names.index(v)
                    mask[i, j] = True
        # Check for model identification: at least 2 variables per factor
        for j, factor_vars in enumerate(self.structure):
            if len([v for v in factor_vars if v in var_names]) < 2:
                raise ValueError(f"Factor {j+1} must have at least 2 variables for identification.")
        # Use ML covariance (divide by N, not N-1)
        S = np.cov(X, rowvar=False, bias=True)
        n_obs = X.shape[0]  # ensure n_obs is N, not N-1
        # Initial values. Fixed-seed RNG so the same model reproduces the same solution.
        rng = np.random.default_rng(0)
        loadings0 = rng.uniform(0.5, 0.8, size=(n_vars, n_factors)) * mask
        # Apply fixed loadings if provided
        for (v, f), val in self.fixed_loadings.items():
            if v in var_names and 0 <= f < n_factors:
                i = var_names.index(v)
                loadings0[i, f] = val
        uniq0 = np.clip(np.diag(S) * 0.5, 1e-4, None)
        phi0 = np.eye(n_factors)
        if self.allow_factor_correlation and n_factors > 1:
            phi0 += 0.2 * (np.ones((n_factors, n_factors)) - np.eye(n_factors))

        # Flatten params
        def pack_params(L, uniq, phi):
            p = []
            for i in range(n_vars):
                for j in range(n_factors):
                    if mask[i, j]:
                        if (var_names[i], j) in self.fixed_loadings:
                            continue
                        p.append(L[i, j])
            p = np.concatenate([p, uniq])
            if self.allow_factor_correlation and n_factors > 1:
                lower_idx = np.tril_indices(n_factors, -1)
                phi_vals = np.arctanh(phi[lower_idx])
                p = np.concatenate([p, phi_vals])
            return p

        def unpack_params(p):
            L = np.zeros((n_vars, n_factors))
            idx = 0
            for i in range(n_vars):
                for j in range(n_factors):
                    if mask[i, j]:
                        if (var_names[i], j) in self.fixed_loadings:
                            L[i, j] = self.fixed_loadings[(var_names[i], j)]
                        else:
                            L[i, j] = p[idx]
                            idx += 1
            uniq = np.clip(p[idx : idx + n_vars], 1e-6, None)
            idx += n_vars
            if self.allow_factor_correlation and n_factors > 1:
                phi = np.eye(n_factors)
                lower_idx = np.tril_indices(n_factors, -1)
                phi_vals = p[idx:]
                phi[lower_idx] = np.tanh(phi_vals)
                phi = phi + phi.T - np.diag(np.diag(phi))
            else:
                phi = np.eye(n_factors)
            return L, uniq, phi

        p0 = pack_params(loadings0, uniq0, phi0)
        # Bounds: loadings unconstrained, uniq [1e-6, inf], phi (-inf, inf) (Fisher z)
        bounds = []
        for i in range(n_vars):
            for j in range(n_factors):
                if mask[i, j]:
                    if (var_names[i], j) in self.fixed_loadings:
                        continue
                    # Standardized loadings: keep within [-1, 1] (a value at the boundary is
                    # already a Heywood case) so they can't blow up while Phi compensates.
                    bounds.append((-1.0, 1.0))
        for _ in range(n_vars):
            bounds.append((1e-6, None))
        if self.allow_factor_correlation and n_factors > 1:
            n_phi = int(n_factors * (n_factors - 1) / 2)
            for _ in range(n_phi):
                # Bound in Fisher-z space so |correlation| <= tanh(2.5) ~= .987, i.e. keep
                # Phi away from the singular +/-1 boundary.
                bounds.append((-2.5, 2.5))

        # Negative log-likelihood
        def nll(p):
            L, uniq, phi = unpack_params(p)
            Sigma = L @ phi @ L.T + np.diag(uniq)
            try:
                sign, logdet = np.linalg.slogdet(Sigma)
                if sign <= 0:
                    return 1e10
                inv_Sigma = np.linalg.inv(Sigma)
                tr = np.trace(S @ inv_Sigma)
                nll_val = logdet + tr
                return nll_val
            except Exception:
                return 1e10

        res = minimize(nll, p0, method="L-BFGS-B", bounds=bounds, options={"maxiter": self.max_iter, "ftol": self.tol})
        converged = res.success
        message = res.message
        L, uniq, phi = unpack_params(res.x)
        # Sign-normalise each factor so its dominant loading direction is positive (a
        # factor's sign is otherwise arbitrary). Sigma = L phi L' is invariant to this.
        for j in range(n_factors):
            if np.sum(L[:, j]) < 0:
                L[:, j] *= -1
                phi[j, :] *= -1
                phi[:, j] *= -1
        # Fit indices
        Sigma = L @ phi @ L.T + np.diag(uniq)
        sign, logdet_S = np.linalg.slogdet(S)
        sign2, logdet_Sigma = np.linalg.slogdet(Sigma)
        tr = np.trace(np.linalg.solve(Sigma, S))
        chi2_stat = n_obs * (logdet_Sigma - logdet_S + tr - n_vars)  # use N, not N-1
        n_params = np.sum(mask) + n_vars
        if self.allow_factor_correlation and n_factors > 1:
            n_params += n_factors * (n_factors - 1) // 2
        df = (n_vars * (n_vars + 1)) // 2 - n_params
        p_value = 1 - chi2.cdf(chi2_stat, df) if df > 0 else np.nan
        rmsea = np.sqrt(max((chi2_stat - df) / (df * n_obs), 0)) if df > 0 else np.nan
        # Null model
        S_diag = np.diag(np.diag(S))
        sign3, logdet_S_diag = np.linalg.slogdet(S_diag)
        tr_null = np.trace(np.linalg.solve(S_diag, S))
        chi2_null = n_obs * (logdet_S_diag - logdet_S + tr_null - n_vars)
        df_null = (n_vars * (n_vars - 1)) // 2
        cfi = 1 - max(chi2_stat - df, 0) / max(chi2_null - df_null, 0) if df > 0 and df_null > 0 else np.nan
        tli = (
            ((chi2_null / df_null) - (chi2_stat / df)) / ((chi2_null / df_null) - 1)
            if df > 0 and df_null > 0
            else np.nan
        )
        # SRMR
        resid = S - Sigma
        srmr = np.sqrt(np.mean((resid / (np.sqrt(np.outer(np.diag(S), np.diag(S))))) ** 2))
        # Standardized loadings (model-implied)
        std_loadings = L / np.sqrt(np.diag(Sigma))[:, None]
        # Standardized residuals
        std_resid = resid / np.sqrt(np.outer(np.diag(S), np.diag(Sigma)))
        fit_indices = {
            "Chi-square": chi2_stat,
            "df": df,
            "p-value": p_value,
            "RMSEA": rmsea,
            "CFI": cfi,
            "TLI": tli,
            "SRMR": srmr,
        }
        return CFAResultStruct(L, phi, uniq, fit_indices, converged, message, std_loadings, std_resid)
