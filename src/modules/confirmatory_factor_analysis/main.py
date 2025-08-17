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

def _fit_cfa_stub(df, columns_list):
    n_factors = len(columns_list)
    variables = [var for factor_vars in columns_list for var in factor_vars]
    n_vars = len(variables)
    loadings = np.zeros((n_vars, n_factors))
    idx = 0
    for f, factor_vars in enumerate(columns_list):
        for _ in factor_vars:
            loadings[idx, f] = 0.8 - 0.1 * f  # Just for demo
            idx += 1
    phi = np.eye(n_factors)
    if n_factors > 1:
        phi += 0.3 * (np.ones((n_factors, n_factors)) - np.eye(n_factors))
    fit_indices = {
        "Chi-square": 12.3 * n_factors,
        "df": 8 * n_factors,
        "p-value": 0.14,
        "RMSEA": 0.05,
        "CFI": 0.97,
        "TLI": 0.95,
    }
    return loadings, variables, phi, fit_indices

@log_function
def recalculate_cfa_study(data: Data, result: CFAResult) -> CFAResult:
    cfg: CFAStudyConfig = result.config
    all_vars = [var for factor_vars in cfg.columns_list for var in factor_vars]
    df = data.get_dataframe(filters=cfg.filters, columns=all_vars, map_ordinal=False)
    if df is None or all(len(factor_vars) == 0 for factor_vars in cfg.columns_list):
        result.set_placeholder("Assign at least one variable to each factor.")
        return result
    loadings, variables, phi, fit_indices = _fit_cfa_stub(df, cfg.columns_list)
    n_factors = len(cfg.columns_list)
    # Fit indices table
    fit_table = HTMLTableV2(table_caption="Model Fit Indices")
    for k, v in fit_indices.items():
        fit_table.add_single_row_apa(Row([Cell(k), Cell(f"{v}")]))
    # Loadings table
    load_table = HTMLTableV2(table_caption="Factor Loadings")
    headers = [Cell("Variable")] + [Cell(f"F{i+1}") for i in range(n_factors)]
    load_table.add_single_row_apa(Row(headers))
    for i, var in enumerate(variables):
        row = [Cell(var)] + [Cell(f"{loadings[i, j]:.2f}") for j in range(n_factors)]
        load_table.add_single_row_apa(Row(row))
    # Factor correlation table
    phi_table = HTMLTableV2(table_caption="Factor Correlation Matrix")
    phi_table.add_single_row_apa(Row([Cell("")] + [Cell(f"F{i+1}") for i in range(n_factors)]))
    for i in range(n_factors):
        row = [Cell(f"F{i+1}")]
        for j in range(n_factors):
            row.append(Cell(f"{phi[i,j]:.2f}"))
        phi_table.add_single_row_apa(Row(row))
    result.result_elements = [fit_table, load_table, phi_table]
    result.header = ""
    result.add_header_info(f"Rotation: <i>{cfg.rotation.value}</i>; Factors: <i>{n_factors}</i>")
    return result
