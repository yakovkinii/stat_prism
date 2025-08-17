import numpy as np
import pandas as pd
from factor_analyzer import FactorAnalyzer
from scipy.stats import chi2

from src.common.decorators import log_function
from src.data.data import Data
from src.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.modules.confirmatory_factor_analysis.result import (
    CFAResult,
    CFAStudyConfig,
)




def _calculate_fit_indices(X, fa, n_factors):
    # Model-implied covariance
    loadings = fa.loadings_
    phi = fa.phi_ if hasattr(fa, "phi_") and fa.phi_ is not None else np.eye(n_factors)
    uniq = fa.get_uniquenesses()
    Sigma_hat = loadings @ phi @ loadings.T + np.diag(uniq)
    S = np.cov(X, rowvar=False)
    n = X.shape[0]
    p = X.shape[1]
    # Chi-square statistic
    try:
        inv_Sigma_hat = np.linalg.inv(Sigma_hat)
        logdet_S = np.linalg.slogdet(S)[1]
        logdet_Sigma_hat = np.linalg.slogdet(Sigma_hat)[1]
        tr = np.trace(S @ inv_Sigma_hat)
        chi2_stat = n * (logdet_Sigma_hat - logdet_S + tr - p)
        df = (p * (p + 1)) // 2 - (p * n_factors + n_factors * (n_factors - 1) // 2)
        p_value = 1 - chi2.cdf(chi2_stat, df) if df > 0 else None
    except Exception:
        chi2_stat, df, p_value = None, None, None
    # RMSEA
    rmsea = None
    if chi2_stat is not None and df and df > 0:
        rmsea = ((max(chi2_stat - df, 0) / (df * n))) ** 0.5
    # CFI, TLI (Bentler's definitions)
    try:
        S_diag = np.diag(np.diag(S))
        inv_S_diag = np.linalg.inv(S_diag)
        tr_null = np.trace(S @ inv_S_diag)
        logdet_S_diag = np.linalg.slogdet(S_diag)[1]
        chi2_null = n * (logdet_S_diag - logdet_S + tr_null - p)
        df_null = (p * (p - 1)) // 2
        cfi = None
        tli = None
        denom_cfi = max(chi2_null - df_null, 0)
        denom_tli = (chi2_null / df_null - 1) if df_null else None
        if chi2_stat is not None and denom_cfi > 0:
            cfi_raw = 1 - max(chi2_stat - df, 0) / denom_cfi
            cfi = min(max(cfi_raw, 0), 1)  # Clamp to [0, 1]
        if chi2_stat is not None and df and df_null and denom_tli and denom_tli > 0:
            tli_raw = ((chi2_null / df_null) - (chi2_stat / df)) / denom_tli
            tli = min(max(tli_raw, 0), 1)  # Clamp to [0, 1]
    except Exception:
        cfi, tli = None, None
    return {
        "Chi-square": f"{chi2_stat:.2f}" if chi2_stat is not None else "-",
        "df": f"{df}" if df is not None else "-",
        "p-value": f"{p_value:.4f}" if p_value is not None else "-",
        "RMSEA": f"{rmsea:.3f}" if rmsea is not None else "-",
        "CFI": f"{cfi:.3f}" if cfi is not None else "-",
        "TLI": f"{tli:.3f}" if tli is not None else "-",
    }


def _fit_quality_text(fit_indices):
    try:
        chi2 = float(fit_indices["Chi-square"])
        df = int(fit_indices["df"])
        p = float(fit_indices["p-value"])
        rmsea = float(fit_indices["RMSEA"])
        cfi = float(fit_indices["CFI"])
        tli = float(fit_indices["TLI"])
    except Exception:
        return "Model fit could not be assessed."
    # If chi2 is nan, force all to nan
    if np.isnan(chi2):
        return "Model fit could not be assessed (fit indices are not available)."
    # Model fit assessment
    fit_text = "<div>"
    if df > 0 and p < 0.05:
        fit_text += "Model fit is poor (Chi-square test significant, p < 0.05)."
    else:
        fit_text += "Model fit is acceptable (Chi-square test not significant, p ≥ 0.05)."
    # RMSEA
    if not np.isnan(rmsea):
        if rmsea < 0.05:
            fit_text += "<br>RMSEA indicates close fit (&lt;0.05)."
        elif rmsea < 0.08:
            fit_text += "<br>RMSEA indicates reasonable fit (&lt;0.08)."
        else:
            fit_text += "<br>RMSEA indicates poor fit (≥0.08)."
    else:
        fit_text += "<br>RMSEA not available."
    # CFI
    if not np.isnan(cfi):
        if cfi >= 0.95:
            fit_text += "<br>CFI indicates excellent fit (≥0.95)."
        elif cfi >= 0.90:
            fit_text += "<br>CFI indicates acceptable fit (≥0.90)."
        else:
            fit_text += "<br>CFI indicates poor fit (&lt;0.90)."
    else:
        fit_text += "<br>CFI not available."
    # TLI
    if not np.isnan(tli):
        if tli >= 0.95:
            fit_text += "<br>TLI indicates excellent fit (≥0.95)."
        elif tli >= 0.90:
            fit_text += "<br>TLI indicates acceptable fit (≥0.90)."
        else:
            fit_text += "<br>TLI indicates poor fit (&lt;0.90)."
    else:
        fit_text += "<br>TLI not available."
    fit_text += "</div>"
    return fit_text


def _safe_float(val):
    try:
        f = float(val)
        if np.isnan(f):
            return np.nan
        return f
    except Exception:
        return np.nan


@log_function
def recalculate_cfa_study(data: Data, result: CFAResult) -> CFAResult:
    cfg: CFAStudyConfig = result.config
    all_vars = [var for factor_vars in cfg.columns_list for var in factor_vars]
    df = data.get_dataframe(filters=cfg.filters, columns=all_vars, map_ordinal=False)
    if df is None or all(len(factor_vars) == 0 for factor_vars in cfg.columns_list):
        result.set_placeholder("Assign at least one variable to each factor.")
        return result
    n_factors = cfg.n_factors
    variables = [var for factor_vars in cfg.columns_list for var in factor_vars]
    if len(variables) < 2 or n_factors < 1:
        result.set_placeholder("At least two variables and one factor required.")
        return result
    X = df.values
    # Determine rotation: oblimin if allow_factor_correlation, else varimax (orthogonal)
    if cfg.allow_factor_correlation:
        rotation = 'oblimin'
    else:
        rotation = 'varimax'
    if cfg.kaiser_normalization:
        rotation_kwargs = {"normalize": True}
    else:
        rotation_kwargs = {"normalize": False}
    # Fit CFA model (using FactorAnalyzer as a proxy for demonstration)
    fa = FactorAnalyzer(
        n_factors=n_factors,
        method="minres",
        rotation=rotation,
        use_smc=True,
        rotation_kwargs=rotation_kwargs,
    )
    try:
        fa.fit(X)
    except Exception as e:
        result.set_placeholder(f"CFA model could not be fit: {e}")
        return result
    loadings = fa.loadings_
    phi = fa.phi_ if hasattr(fa, "phi_") and fa.phi_ is not None else np.eye(n_factors)
    fit_indices = _calculate_fit_indices(X, fa, n_factors)
    # If chi2 is nan, force all to nan
    if _safe_float(fit_indices["Chi-square"]) != _safe_float(fit_indices["Chi-square"]):
        for k in fit_indices:
            fit_indices[k] = "-"
    fit_text = _fit_quality_text(fit_indices)
    # Fit indices table
    fit_table = HTMLTableV2(table_caption="Model Fit Indices")
    for k, v in fit_indices.items():
        fit_table.add_single_row_apa(Row([Cell(k), Cell(f"{v}")]))
    fit_table.add_text(fit_text)
    # Loadings (pattern) table
    load_table = HTMLTableV2(table_caption=f"Factor Loadings ({'oblimin' if cfg.allow_factor_correlation else 'varimax'})")
    headers = [Cell("Variable")] + [Cell(f"F{i+1}") for i in range(n_factors)]
    load_table.add_single_row_apa(Row(headers))
    for idx, var in enumerate(variables):
        row = [Cell(var)] + [Cell(f"{loadings[idx, j]:.3f}") for j in range(n_factors)]
        load_table.add_single_row_apa(Row(row))
    result.result_elements = [fit_table, load_table]
    # Factor correlation (phi) table only if allow_factor_correlation
    if cfg.allow_factor_correlation:
        phi_table = HTMLTableV2(table_caption="Factor Correlation Matrix (Phi)")
        phi_table.add_single_row_apa(Row([Cell("")] + [Cell(f"F{i+1}") for i in range(n_factors)]))
        for i in range(n_factors):
            row = [Cell(f"F{i+1}")]
            for j in range(n_factors):
                row.append(Cell(f"{phi[i, j]:.3f}"))
            phi_table.add_single_row_apa(Row(row))
        result.result_elements.append(phi_table)
    result.header = ""
    result.add_header_info(f"Allow factor correlation: <i>{'Yes' if cfg.allow_factor_correlation else 'No'}</i>; Factors: <i>{n_factors}</i>")
    return result
