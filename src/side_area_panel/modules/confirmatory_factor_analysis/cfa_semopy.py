#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.


import numpy as np
import pandas as pd
import semopy
from scipy.stats import chi2 as _chi2
from semopy.stats import (
    calc_agfi,
    calc_cfi,
    calc_chi2,
    calc_dof,
    calc_gfi,
    calc_nfi,
    calc_rmsea,
    calc_tli,
    get_baseline_model,
)

from src.side_area_panel.modules.confirmatory_factor_analysis.cfa_numpy import CFAResultStruct

# Objective labels exposed to the UI -> semopy `obj` argument.
OBJECTIVE_ML = "Maximum Likelihood (ML)"
OBJECTIVE_DWLS = "Diagonally Weighted LS (DWLS)"
_OBJECTIVE_TO_SEMOPY = {OBJECTIVE_ML: "MLW", OBJECTIVE_DWLS: "DWLS"}
OBJECTIVES = [OBJECTIVE_ML, OBJECTIVE_DWLS]


def _fit_report(S, Sigma):
    """SRMR and standardized residuals -- the two quantities semopy's ``calc_stats`` does not
    provide. ``Sigma`` is the fitted model-implied covariance (semopy's ``calc_sigma``), so it
    reflects a second-order factor, cross-loadings and freed residual covariances. SRMR averages
    the squared standardized residuals over the unique (lower-triangle, diagonal-inclusive)
    elements -- p(p+1)/2 of them, the standard definition. The standardized residuals feed the
    heatmap and modification hints."""
    resid = S - Sigma
    r = resid / np.sqrt(np.outer(np.diag(S), np.diag(S)))
    lower = np.tril_indices_from(r)
    srmr = float(np.sqrt(np.mean(r[lower] ** 2)))
    std_resid = resid / np.sqrt(np.outer(np.diag(S), np.diag(Sigma)))
    return srmr, std_resid


def _sb_scaled_chi2(model, naive_chi2, dof):
    """Satorra-Bentler mean-and-variance-adjusted (WLSMV) rescaling of a fit's naive ``N * F``
    statistic, returning ``(scaled_chi2, scaled_dof)``. Under diagonal weighting the naive statistic
    is a mixture of chi-squares (its mean is not the model df), so it must be rescaled to recover an
    approximately chi-square statistic -- this is the statistically valid test for DWLS.

    Uses semopy's own model matrices: ``mx_w`` is the empirical (ADF, fourth-moment) covariance of
    the sample moments Gamma, the DWLS fit weight is ``diag(Gamma)^-1``, and ``calc_sigma_grad``
    gives the model Jacobian Delta. With ``U = W - W Delta (Delta' W Delta)^-1 Delta' W`` the naive
    statistic has mean ``k1 = tr(U Gamma)`` and variance ``2 k2 = 2 tr((U Gamma)^2)``; matching the
    first two moments of a chi-square gives scaled df ``k1^2 / k2`` and scaled statistic
    ``naive * k1 / k2``."""
    _, (m, c) = model.calc_sigma()
    inds = model.inds_triu_sigma
    delta = np.array([g[inds] for g in model.calc_sigma_grad(m, c)]).T  # (n_moments, n_params)
    gamma = model.mx_w
    weight = np.diag(model.mx_w_inv) if np.ndim(model.mx_w_inv) == 1 else model.mx_w_inv
    wd = weight @ delta
    u = weight - wd @ np.linalg.pinv(delta.T @ wd) @ wd.T
    ug = u @ gamma
    k1 = float(np.trace(ug))
    k2 = float(np.trace(ug @ ug))
    if not (np.isfinite(k1) and np.isfinite(k2)) or k1 <= 0 or k2 <= 0:
        return naive_chi2, dof
    return naive_chi2 * k1 / k2, k1 * k1 / k2


def _semopy_fit_indices(model, srmr):
    """Fit indices from semopy's model, computed the standard (lavaan-style) way so they line up
    with tools such as jamovi and reflect any freed residual covariances.

    For ML this is semopy's own ``calc_stats``. For DWLS the naive ``N * F`` statistic is not
    chi-square distributed, so the model *and* the baseline chi-square are each replaced by their
    Satorra-Bentler mean-and-variance-adjusted (WLSMV) values before the indices are formed. SRMR is
    not part of calc_stats, so it is passed in from the matrix-based computation."""
    is_dwls = str(getattr(model.last_result, "name_obj", "")).upper() == "DWLS"
    if not is_dwls:
        stats = semopy.calc_stats(model).iloc[0]
        return {
            "Chi-square": float(stats["chi2"]),
            "df": float(stats["DoF"]),
            "p-value": float(stats["chi2 p-value"]),
            "RMSEA": float(stats["RMSEA"]),
            "CFI": float(stats["CFI"]),
            "TLI": float(stats["TLI"]),
            "SRMR": srmr,
        }

    dof = calc_dof(model)
    chi2_model, dof = _sb_scaled_chi2(model, calc_chi2(model, dof)[0], dof)

    # The baseline (independence) model is refit with the same objective and rescaled the same way,
    # so CFI / TLI compare like with like.
    base = get_baseline_model(model)
    base.fit(obj=model.last_result.name_obj)
    dof_base = calc_dof(base)
    chi2_base, dof_base = _sb_scaled_chi2(base, calc_chi2(base, dof_base)[0], dof_base)

    p_value = float(1 - _chi2.cdf(chi2_model, dof)) if dof > 0 else np.nan
    rmsea = np.sqrt(max((chi2_model / dof - 1) / (model.n_samples - 1), 0.0)) if dof > 0 else np.nan
    cfi = 1 - max(chi2_model - dof, 0.0) / max(chi2_base - dof_base, 1e-12) if dof_base > 0 else np.nan
    if dof > 0 and dof_base > 0:
        a, b = chi2_model / dof, chi2_base / dof_base
        tli = (b - a) / (b - 1) if b != 1 else np.nan
    else:
        tli = np.nan
    return {
        "Chi-square": float(chi2_model),
        "df": float(dof),
        "p-value": p_value,
        "RMSEA": float(rmsea),
        "CFI": float(cfi),
        "TLI": float(tli),
        "SRMR": srmr,
    }


def calc_stats_scaled(model):
    """``semopy.calc_stats``, but for a DWLS fit every chi-square-derived index (chi2, CFI, TLI,
    RMSEA, GFI, AGFI, NFI) is replaced by its Satorra-Bentler mean-and-variance-adjusted (WLSMV)
    value -- the naive DWLS chi-square is not chi-square distributed, so the raw indices are not
    valid. For ML it is calc_stats unchanged. AIC / BIC / LogLik are likelihood-based and left as
    reported. Shared by the SEM module so its DWLS fit indices are correct too."""
    stats = semopy.calc_stats(model)
    if str(getattr(model.last_result, "name_obj", "")).upper() != "DWLS":
        return stats

    dof = calc_dof(model)
    chi2_model, dof = _sb_scaled_chi2(model, calc_chi2(model, dof)[0], dof)
    base = get_baseline_model(model)
    base.fit(obj=model.last_result.name_obj)
    dof_base = calc_dof(base)
    chi2_base, dof_base = _sb_scaled_chi2(base, calc_chi2(base, dof_base)[0], dof_base)

    row = stats.iloc[0].copy()
    row["DoF"] = dof
    row["DoF Baseline"] = dof_base
    row["chi2"] = chi2_model
    row["chi2 p-value"] = float(1 - _chi2.cdf(chi2_model, dof)) if dof > 0 else np.nan
    row["chi2 Baseline"] = chi2_base
    row["CFI"] = calc_cfi(model, dof, chi2_model, dof_base, chi2_base)
    row["TLI"] = calc_tli(model, dof, chi2_model, dof_base, chi2_base)
    row["RMSEA"] = calc_rmsea(model, chi2_model, dof)
    row["GFI"] = calc_gfi(model, chi2_model, chi2_base)
    row["AGFI"] = calc_agfi(model, dof, dof_base, row["GFI"])
    row["NFI"] = calc_nfi(model, chi2_model, chi2_base)
    return pd.DataFrame([row], index=stats.index)


class CFASemopyEstimator:
    """CFA via semopy. Mirrors :class:`cfa_numpy.CFAEstimator`'s interface."""

    # Name of the general (second-order) factor added when second_order is on.
    SECOND_ORDER = "G"

    def __init__(
        self,
        structure,
        allow_factor_correlation=True,
        objective=OBJECTIVE_ML,
        second_order=False,
        residual_correlations=None,
        **_ignored,
    ):
        self.structure = structure
        self.allow_factor_correlation = allow_factor_correlation
        self.objective = objective
        # A single second-order factor loading on every first-order factor (needs >= 3 factors to
        # be identified). semopy backend only.
        self.second_order = second_order
        # Item pairs whose residual covariance is freed: [[item_a, item_b], ...].
        self.residual_correlations = residual_correlations or []

    def _model_description(self, factor_names, present, residual_pairs=None):
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
        # Free the residual covariance of each requested item pair (measurement errors correlate).
        for alias_a, alias_b in residual_pairs or []:
            lines.append(f"{alias_a} ~~ {alias_b}")
        return "\n".join(lines)

    def fit(self, X, var_names=None):
        X = np.asarray(X, dtype=float)
        if np.isnan(X).any():
            X = X[~np.isnan(X).any(axis=1)]
        # Standardize (fit on the correlation matrix) — matches cfa_numpy so factor variances are 1.
        col_std = X.std(axis=0, ddof=0)
        col_std[col_std == 0] = 1.0
        X = (X - X.mean(axis=0)) / col_std
        n_vars = X.shape[1]
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

        # Map requested residual-correlation pairs to their aliases, keeping only pairs whose
        # two (distinct) items are both in the model.
        residual_pairs = []
        for pair in self.residual_correlations:
            try:
                item_a, item_b = pair[0], pair[1]
            except (TypeError, IndexError):
                continue
            if item_a in alias_of and item_b in alias_of and item_a != item_b:
                residual_pairs.append((alias_of[item_a], alias_of[item_b]))

        data = pd.DataFrame(X, columns=aliases)
        model = semopy.Model(self._model_description(factor_names, present, residual_pairs))
        obj = _OBJECTIVE_TO_SEMOPY.get(self.objective, "MLW")
        res = model.fit(data, obj=obj)
        converged = bool(getattr(res, "success", True))
        message = str(getattr(res, "name_method", obj))

        insp = model.inspect(std_est=True)

        # Parse the estimates into the L / phi / uniq matrices this app reports on. Indicators
        # come back as aliases; factors keep their F1/F2/G names.
        n_factors = len(factor_names)
        factor_index = {f: j for j, f in enumerate(factor_names)}
        L = np.zeros((n_vars, n_factors))  # raw (unstandardized) loadings, used for uniqueness fill
        std_L = np.zeros((n_vars, n_factors))  # standardized loadings (reported), from semopy
        loading_se = np.full((n_vars, n_factors), np.nan)
        phi = np.eye(n_factors)  # raw factor covariance, used only for the uniqueness fill below
        std_phi = np.eye(n_factors)  # standardized factor correlations (reported), from semopy
        uniq = np.full(n_vars, np.nan)
        second_order = {}  # first-order factor name -> standardized loading on G

        for _, row in insp.iterrows():
            lval, op, rval = row["lval"], row["op"], row["rval"]
            est = _to_float(row.get("Estimate"))
            # semopy's own standardized estimate (raw * factor SD / indicator SD): the correct
            # standardized loading (~ -1..1). Deriving it as L / sqrt(diag(Sigma)) drops the factor
            # SD and inflates it whenever a factor's variance is not 1 (e.g. with DWLS).
            est_std = _to_float(row.get("Est. Std"))
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
                    std_L[alias_index[indicator], factor_index[factor]] = est_std
                    loading_se[alias_index[indicator], factor_index[factor]] = se
                    continue
                # Second-order loading: the general factor G on a first-order factor.
                if lval == self.SECOND_ORDER and rval in factor_index:
                    second_order[rval] = est_std
                elif rval == self.SECOND_ORDER and lval in factor_index:
                    second_order[lval] = est_std
            elif op == "~~":
                if lval in alias_index and rval == lval:
                    uniq[alias_index[lval]] = est  # residual (unique) variance
                elif lval in factor_index and rval in factor_index and lval != rval:
                    i, j = factor_index[lval], factor_index[rval]
                    phi[i, j] = phi[j, i] = est
                    std_phi[i, j] = std_phi[j, i] = est_std

        # Fill any uniqueness semopy did not report from the model-implied common variance.
        for i in range(n_vars):
            if np.isnan(uniq[i]):
                uniq[i] = max(1.0 - float(L[i] @ phi @ L[i].T), 1e-6)
        uniq = np.clip(uniq, 1e-6, None)

        # Sign-normalise each factor (its sign is arbitrary; Sigma is invariant).
        for j in range(n_factors):
            if np.sum(L[:, j]) < 0:
                L[:, j] *= -1
                std_L[:, j] *= -1
                std_phi[j, :] *= -1
                std_phi[:, j] *= -1

        S = np.cov(X, rowvar=False, bias=True)
        sigma_model = model.calc_sigma()[0]
        srmr, std_resid = _fit_report(S, sigma_model)
        # Fit indices come from semopy (ML) or the Satorra-Bentler scaling (DWLS). If that raises,
        # the study fails and shows an error -- no silent fallback to an invalid matrix computation.
        fit_indices = _semopy_fit_indices(model, srmr)

        second_order_loadings = None
        if self.second_order and second_order:
            second_order_loadings = [(name, second_order[name]) for name in factor_names if name in second_order]

        return CFAResultStruct(
            L,
            std_phi,
            uniq,
            fit_indices,
            converged,
            message,
            std_L,
            std_resid,
            loading_se,
            second_order_loadings=second_order_loadings,
        )


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return np.nan
