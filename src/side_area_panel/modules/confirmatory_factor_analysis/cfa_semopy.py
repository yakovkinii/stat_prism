#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""semopy-backed CFA estimator.

This is a drop-in replacement for :class:`cfa_numpy.CFAEstimator`: same constructor shape and
``fit(X, var_names)`` contract, same :class:`cfa_numpy.CFAResultStruct` return type — so the CFA
module can switch backends with no other changes.

Design choice: semopy is used **only to estimate the parameters** (it brings the robust solvers
and the DWLS objective we want). Everything reported — the model-implied covariance, χ²/df/p,
RMSEA, CFI, TLI, SRMR and the standardized loadings/residuals — is then recomputed here from the
parsed loadings / factor correlations / uniquenesses with the *same formulas* the hand-rolled
estimator uses. That keeps one source of truth for the fit maths and means a backend switch does
not change how a given solution is summarised.

semopy is a hard dependency: it is imported at module top level, so a missing package fails fast
at import time rather than being silently worked around.

    !! Not yet validated end-to-end (the environment this was written in cannot run Python). The
       semopy ``inspect()`` column names (``lval``/``op``/``rval``/``Estimate``/``Std. Err``) and
       the ``obj`` argument follow semopy 2.3.x; verify against the installed version.
"""

import numpy as np
import pandas as pd
import semopy
from scipy.stats import chi2 as _chi2

from src.side_area_panel.modules.confirmatory_factor_analysis.cfa_numpy import CFAResultStruct

# Objective labels exposed to the UI -> semopy `obj` argument.
OBJECTIVE_ML = "Maximum Likelihood (ML)"
OBJECTIVE_DWLS = "Diagonally Weighted LS (DWLS)"
_OBJECTIVE_TO_SEMOPY = {OBJECTIVE_ML: "MLW", OBJECTIVE_DWLS: "DWLS"}
OBJECTIVES = [OBJECTIVE_ML, OBJECTIVE_DWLS]


def _fit_report(S, L, phi, uniq, n_obs, n_params):
    """Fit indices + standardized quantities from the model matrices — identical maths to
    ``cfa_numpy`` so the two backends summarise a solution the same way."""
    n_vars = S.shape[0]
    Sigma = L @ phi @ L.T + np.diag(uniq)
    _, logdet_S = np.linalg.slogdet(S)
    _, logdet_Sigma = np.linalg.slogdet(Sigma)
    tr = np.trace(np.linalg.solve(Sigma, S))
    chi2_stat = n_obs * (logdet_Sigma - logdet_S + tr - n_vars)

    df = (n_vars * (n_vars + 1)) // 2 - n_params
    p_value = 1 - _chi2.cdf(chi2_stat, df) if df > 0 else np.nan
    rmsea = np.sqrt(max((chi2_stat - df) / (df * n_obs), 0)) if df > 0 else np.nan

    # Null (independence) model.
    S_diag = np.diag(np.diag(S))
    _, logdet_S_diag = np.linalg.slogdet(S_diag)
    tr_null = np.trace(np.linalg.solve(S_diag, S))
    chi2_null = n_obs * (logdet_S_diag - logdet_S + tr_null - n_vars)
    df_null = (n_vars * (n_vars - 1)) // 2
    cfi = 1 - max(chi2_stat - df, 0) / max(chi2_null - df_null, 0) if df > 0 and df_null > 0 else np.nan
    tli = ((chi2_null / df_null) - (chi2_stat / df)) / ((chi2_null / df_null) - 1) if df > 0 and df_null > 0 else np.nan

    resid = S - Sigma
    srmr = np.sqrt(np.mean((resid / np.sqrt(np.outer(np.diag(S), np.diag(S)))) ** 2))
    std_loadings = L / np.sqrt(np.diag(Sigma))[:, None]
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
    return fit_indices, std_loadings, std_resid


class CFASemopyEstimator:
    """CFA via semopy. Mirrors :class:`cfa_numpy.CFAEstimator`'s interface."""

    # Name of the general (second-order) factor added when second_order is on.
    SECOND_ORDER = "G"

    def __init__(
        self, structure, allow_factor_correlation=True, objective=OBJECTIVE_ML, second_order=False, **_ignored
    ):
        self.structure = structure
        self.allow_factor_correlation = allow_factor_correlation
        self.objective = objective
        # A single second-order factor loading on every first-order factor (needs >= 3 factors to
        # be identified). semopy backend only.
        self.second_order = second_order

    def _model_description(self, factor_names, present):
        lines = []
        for name, indicators in zip(factor_names, present):
            lines.append(f"{name} =~ " + " + ".join(indicators))
        if self.second_order and len(factor_names) >= 3:
            # Higher-order factor explaining the first-order factors' covariances.
            lines.append(f"{self.SECOND_ORDER} =~ " + " + ".join(factor_names))
        elif not self.allow_factor_correlation and len(factor_names) > 1:
            # Orthogonal model: fix every factor covariance to 0 (semopy correlates by default).
            for i in range(len(factor_names)):
                for j in range(i + 1, len(factor_names)):
                    lines.append(f"{factor_names[i]} ~~ 0*{factor_names[j]}")
        return "\n".join(lines)

    def fit(self, X, var_names=None):
        X = np.asarray(X, dtype=float)
        if np.isnan(X).any():
            X = X[~np.isnan(X).any(axis=1)]
        # Standardize (fit on the correlation matrix) — matches cfa_numpy so factor variances are 1.
        col_std = X.std(axis=0, ddof=0)
        col_std[col_std == 0] = 1.0
        X = (X - X.mean(axis=0)) / col_std
        n_obs, n_vars = X.shape
        if var_names is None:
            var_names = [f"x{i + 1}" for i in range(n_vars)]

        # semopy's model syntax cannot handle real column names that contain spaces, "+", digits
        # or punctuation (survey items are whole sentences). Fit on safe positional aliases
        # (v0, v1, …) and map the parsed estimates back by position.
        aliases = [f"v{i}" for i in range(n_vars)]
        alias_of = {var_names[i]: aliases[i] for i in range(n_vars)}
        alias_index = {aliases[i]: i for i in range(n_vars)}

        factor_names = [f"F{i + 1}" for i in range(len(self.structure))]
        present = []
        for j, factor_vars in enumerate(self.structure):
            cols = [alias_of[v] for v in factor_vars if v in alias_of]
            if len(cols) < 2:
                raise ValueError(f"Factor {j + 1} must have at least 2 variables for identification.")
            present.append(cols)

        data = pd.DataFrame(X, columns=aliases)
        model = semopy.Model(self._model_description(factor_names, present))
        obj = _OBJECTIVE_TO_SEMOPY.get(self.objective, "MLW")
        res = model.fit(data, obj=obj)
        converged = bool(getattr(res, "success", True))
        message = str(getattr(res, "name_method", obj))

        insp = model.inspect(std_est=True)

        # Parse the estimates into the L / phi / uniq matrices this app reports on. Indicators
        # come back as aliases; factors keep their F1/F2/G names.
        n_factors = len(factor_names)
        factor_index = {f: j for j, f in enumerate(factor_names)}
        L = np.zeros((n_vars, n_factors))
        loading_se = np.full((n_vars, n_factors), np.nan)
        phi = np.eye(n_factors)
        uniq = np.full(n_vars, np.nan)
        second_order = {}  # first-order factor name -> loading on G

        for _, row in insp.iterrows():
            lval, op, rval = row["lval"], row["op"], row["rval"]
            est = _to_float(row.get("Estimate"))
            se = _to_float(row.get("Std. Err"))

            if op in ("=~", "~"):
                # semopy reports a loading as "indicator ~ factor" (op '~', indicator on the left);
                # accept either operator and either orientation so parsing is convention-proof.
                if lval in factor_index and rval in alias_index:
                    factor, indicator = lval, rval
                elif rval in factor_index and lval in alias_index:
                    factor, indicator = rval, lval
                else:
                    factor = indicator = None
                if factor is not None:
                    L[alias_index[indicator], factor_index[factor]] = est
                    loading_se[alias_index[indicator], factor_index[factor]] = se
                    continue
                # Second-order loading: the general factor G on a first-order factor.
                if lval == self.SECOND_ORDER and rval in factor_index:
                    second_order[rval] = est
                elif rval == self.SECOND_ORDER and lval in factor_index:
                    second_order[lval] = est
            elif op == "~~":
                if lval in alias_index and rval == lval:
                    uniq[alias_index[lval]] = est  # residual (unique) variance
                elif lval in factor_index and rval in factor_index and lval != rval:
                    i, j = factor_index[lval], factor_index[rval]
                    phi[i, j] = phi[j, i] = est

        # Fill any uniqueness semopy did not report from the model-implied common variance.
        for i in range(n_vars):
            if np.isnan(uniq[i]):
                uniq[i] = max(1.0 - float(L[i] @ phi @ L[i].T), 1e-6)
        uniq = np.clip(uniq, 1e-6, None)

        # Sign-normalise each factor (its sign is arbitrary; Sigma is invariant).
        for j in range(n_factors):
            if np.sum(L[:, j]) < 0:
                L[:, j] *= -1
                phi[j, :] *= -1
                phi[:, j] *= -1

        S = np.cov(X, rowvar=False, bias=True)
        n_params = int(np.count_nonzero(L)) + n_vars
        if self.allow_factor_correlation and n_factors > 1:
            n_params += n_factors * (n_factors - 1) // 2
        fit_indices, std_loadings, std_resid = _fit_report(S, L, phi, uniq, n_obs, n_params)

        second_order_loadings = None
        if self.second_order and second_order:
            second_order_loadings = [(name, second_order[name]) for name in factor_names if name in second_order]

        return CFAResultStruct(
            L,
            phi,
            uniq,
            fit_indices,
            converged,
            message,
            std_loadings,
            std_resid,
            loading_se,
            second_order_loadings=second_order_loadings,
        )


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan
