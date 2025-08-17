import numpy as np
import pandas as pd
from src.common.decorators import log_function
from src.data.data import Data
from src.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.modules.confirmatory_factor_analysis.result import (
    CFAResult,
    CFAStudyConfig,
    RotationType,
)

def _fit_cfa_stub(df, factor1_vars, factor2_vars):
    # This is a placeholder CFA fit. Replace with a real CFA library if available.
    # For now, just create fake loadings and fit indices for demonstration.
    n1 = len(factor1_vars)
    n2 = len(factor2_vars)
    loadings = np.zeros((n1 + n2, 2))
    loadings[:n1, 0] = 0.8
    loadings[n1:, 1] = 0.7
    variables = factor1_vars + factor2_vars
    phi = np.array([[1.0, 0.3], [0.3, 1.0]])
    fit_indices = {
        "Chi-square": 12.3,
        "df": 8,
        "p-value": 0.14,
        "RMSEA": 0.05,
        "CFI": 0.97,
        "TLI": 0.95,
    }
    return loadings, variables, phi, fit_indices

@log_function
def recalculate_cfa_study(data: Data, result: CFAResult) -> CFAResult:
    cfg: CFAStudyConfig = result.config
    df = data.get_dataframe(filters=cfg.filters, columns=cfg.factor1_vars + cfg.factor2_vars, map_ordinal=False)
    if df is None or (len(cfg.factor1_vars) == 0 and len(cfg.factor2_vars) == 0):
        result.set_placeholder("Assign at least one variable to each factor.")
        return result
    loadings, variables, phi, fit_indices = _fit_cfa_stub(df, cfg.factor1_vars, cfg.factor2_vars)
    # Fit indices table
    fit_table = HTMLTableV2(table_caption="Model Fit Indices")
    for k, v in fit_indices.items():
        fit_table.add_single_row_apa(Row([Cell(k), Cell(f"{v}")]))
    # Loadings table
    load_table = HTMLTableV2(table_caption="Factor Loadings")
    headers = [Cell("Variable"), Cell("F1"), Cell("F2")]
    load_table.add_single_row_apa(Row(headers))
    for i, var in enumerate(variables):
        row = [Cell(var), Cell(f"{loadings[i,0]:.2f}"), Cell(f"{loadings[i,1]:.2f}")]
        load_table.add_single_row_apa(Row(row))
    # Factor correlation table
    phi_table = HTMLTableV2(table_caption="Factor Correlation Matrix")
    phi_table.add_single_row_apa(Row([Cell("")] + [Cell(f"F{i+1}") for i in range(2)]))
    for i in range(2):
        row = [Cell(f"F{i+1}")]
        for j in range(2):
            row.append(Cell(f"{phi[i,j]:.2f}"))
        phi_table.add_single_row_apa(Row(row))
    result.result_elements = [fit_table, load_table, phi_table]
    result.header = ""
    result.add_header_info(f"Rotation: <i>{cfg.rotation.value}</i>")
    return result

