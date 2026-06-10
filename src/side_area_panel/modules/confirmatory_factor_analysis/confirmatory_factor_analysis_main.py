import numpy as np
import pandas as pd

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.confirmatory_factor_analysis.cfa_numpy import (
    CFAEstimator,
)
from src.side_area_panel.modules.confirmatory_factor_analysis.confirmatory_factor_analysis_result import (
    CFAResult,
    CFAStudyConfig,
)


def _fit_quality_text(fit_indices):
    try:
        chi2 = float(fit_indices["Chi-square"])
        df = int(fit_indices["df"])
        p = float(fit_indices["p-value"])
        rmsea = float(fit_indices["RMSEA"])
        cfi = float(fit_indices["CFI"])
        tli = float(fit_indices["TLI"])
    except Exception:
        return "<div>Model fit could not be assessed.</div>"
    if np.isnan(chi2):
        return "<div>Model fit could not be assessed (fit indices are not available).</div>"
    fit_text = "<div>"
    if df > 0 and p < 0.05:
        fit_text += "Model fit is poor (Chi-square test significant, p &lt; 0.05)."
    else:
        fit_text += "Model fit is acceptable (Chi-square test not significant, p &ge; 0.05)."
    if not np.isnan(rmsea):
        if rmsea < 0.05:
            fit_text += "<br>RMSEA indicates close fit (&lt;0.05)."
        elif rmsea < 0.08:
            fit_text += "<br>RMSEA indicates reasonable fit (&lt;0.08)."
        else:
            fit_text += "<br>RMSEA indicates poor fit (&ge;0.08)."
    else:
        fit_text += "<br>RMSEA not available."
    if not np.isnan(cfi):
        if cfi >= 0.95:
            fit_text += "<br>CFI indicates excellent fit (&ge;0.95)."
        elif cfi >= 0.90:
            fit_text += "<br>CFI indicates acceptable fit (&ge;0.90)."
        else:
            fit_text += "<br>CFI indicates poor fit (&lt;0.90)."
    else:
        fit_text += "<br>CFI not available."
    if not np.isnan(tli):
        if tli >= 0.95:
            fit_text += "<br>TLI indicates excellent fit (&ge;0.95)."
        elif tli >= 0.90:
            fit_text += "<br>TLI indicates acceptable fit (&ge;0.90)."
        else:
            fit_text += "<br>TLI indicates poor fit (&lt;0.90)."
    else:
        fit_text += "<br>TLI not available."
    fit_text += "</div>"
    return fit_text


@log_function
def recalculate_cfa_study(elements, result: CFAResult) -> CFAResult:
    cfg: CFAStudyConfig = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    all_vars = [var for factor_vars in cfg.column_selector for var in factor_vars]
    df = data.get_dataframe(columns=all_vars, map_ordinal=False)
    if df is None or all(len(factor_vars) == 0 for factor_vars in cfg.column_selector):
        result.set_placeholder("Assign at least one variable to each factor.")
        return result
    n_factors = cfg.n_factors
    variables = [var for factor_vars in cfg.column_selector for var in factor_vars]
    if len(variables) < 2 or n_factors < 1:
        result.set_placeholder("At least two variables and one factor required.")
        return result
    X = df.values
    # Use new CFAEstimator
    structure = cfg.column_selector
    estimator = CFAEstimator(structure=structure, allow_factor_correlation=cfg.allow_factor_correlation)
    try:
        cfa_result = estimator.fit(X, var_names=list(df.columns))
    except Exception as e:
        result.set_placeholder(f"CFA model could not be fit: {e}")
        return result
    loadings = cfa_result.loadings_
    phi = cfa_result.phi_
    fit_indices = {
        "Chi-square": f"{cfa_result.fit_indices_['Chi-square']:.2f}"
        if cfa_result.fit_indices_["Chi-square"] is not None
        else "-",
        "df": f"{cfa_result.fit_indices_['df']}" if cfa_result.fit_indices_["df"] is not None else "-",
        "p-value": f"{cfa_result.fit_indices_['p-value']:.4f}"
        if cfa_result.fit_indices_["p-value"] is not None
        else "-",
        "RMSEA": f"{cfa_result.fit_indices_['RMSEA']:.3f}" if cfa_result.fit_indices_["RMSEA"] is not None else "-",
        "CFI": f"{cfa_result.fit_indices_['CFI']:.3f}" if cfa_result.fit_indices_["CFI"] is not None else "-",
        "TLI": f"{cfa_result.fit_indices_['TLI']:.3f}" if cfa_result.fit_indices_["TLI"] is not None else "-",
        "SRMR": f"{cfa_result.fit_indices_['SRMR']:.3f}" if cfa_result.fit_indices_["SRMR"] is not None else "-",
    }

    def _safe_float(val):
        try:
            f = float(val)
            if np.isnan(f):
                return np.nan
            return f
        except Exception:
            return np.nan

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
    factor_names = [f"F{i+1}" for i in range(n_factors)]
    headers = [Cell("Variable")] + [Cell(f) for f in factor_names]
    load_table = HTMLTableV2(table_caption="Factor Loadings")
    load_table.add_single_row_apa(Row(headers))
    for idx, var in enumerate(df.columns):
        row = [Cell(var)]
        for j in range(n_factors):
            row.append(Cell(f"{loadings[idx, j]:.3f}"))
        load_table.add_single_row_apa(Row(row))
    result.result_elements = [fit_table, load_table]
    # Add heatmap of factor loadings (like EFA)
    factor_names = [f"F{i+1}" for i in range(n_factors)]
    loadings_df = pd.DataFrame(loadings, index=df.columns, columns=factor_names)
    from src.side_area_panel.modules.common.result.plot_result import Heatmap, PlotV2

    heatmap = Heatmap(df=loadings_df, p=None, label="Factor Loadings Heatmap")
    heatmap_plot = PlotV2(
        items=[heatmap],
        title="Factor Loadings Heatmap",
        plot_title="Factor Loadings Heatmap",
        x_axis_title="Factors",
        y_axis_title="Variables",
    )
    result.result_elements.append(heatmap_plot)
    # Factor correlation (phi) table only if allow_factor_correlation
    if cfg.allow_factor_correlation:
        phi_table = HTMLTableV2(table_caption="Factor Correlation Matrix (Phi)")
        phi_table.add_single_row_apa(Row([Cell("")] + [Cell(f) for f in factor_names]))
        for i in range(n_factors):
            row = [Cell(factor_names[i])]
            for j in range(n_factors):
                row.append(Cell(f"{phi[i, j]:.3f}"))
            phi_table.add_single_row_apa(Row(row))
        result.result_elements.append(phi_table)
    result.header = ""
    result.add_header_info(
        f"Allow factor correlation: <i>{'Yes' if cfg.allow_factor_correlation else 'No'}</i>; "
        f"Factors: <i>{n_factors}</i>"
    )
    return result
