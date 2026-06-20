#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

import numpy as np
import pandas as pd
from scipy.stats import norm

from src.common.decorators import log_function
from src.common.translations import t
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.column_numbering import ColumnNumbering
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.result.plot_result import Heatmap, PlotV2
from src.side_area_panel.modules.common.utility import (
    format_p_apa_exact,
    format_p_apa_full,
    format_r_apa,
    format_statistic_apa,
    get_stars,
)
from src.side_area_panel.modules.confirmatory_factor_analysis.cfa_numpy import CFAEstimator
from src.side_area_panel.modules.confirmatory_factor_analysis.confirmatory_factor_analysis_result import (
    CFAResult,
    CFAStudyConfig,
)


def _fail(result: CFAResult, message: str) -> CFAResult:
    """Show a validation message to the user and log it, then stop."""
    logging.warning("CFA: %s", message)
    result.set_error(message)
    return result


def _is_nan(value) -> bool:
    return value is None or (isinstance(value, float) and np.isnan(value))


def _fmt(value, decimals: int = 3) -> str:
    return "—" if _is_nan(value) else format_statistic_apa(value, decimals)


def _interpretation_key(name: str, value) -> str:
    """Fit-index quality label key (or None for raw statistics like χ²/df)."""
    if _is_nan(value):
        return None
    if name == "RMSEA":
        if value < 0.05:
            return "good"
        if value < 0.08:
            return "acceptable"
        if value < 0.10:
            return "mediocre"
        return "poor"
    if name in ("CFI", "TLI"):
        if value >= 0.95:
            return "excellent"
        if value >= 0.90:
            return "acceptable"
        return "poor"
    if name == "SRMR":
        return "good" if value <= 0.08 else "poor"
    if name == "p":  # exact-fit chi-square test
        return "good" if value >= 0.05 else "poor"
    return None


def _label(name: str, value) -> str:
    key = _interpretation_key(name, value)
    return t(f"cfa.fit.{key}") if key else "—"


def _fit_prose(fit: dict, converged: bool) -> str:
    text = "" if converged else t("cfa.report.not_converged")
    chi2, df, p = fit["Chi-square"], fit["df"], fit["p-value"]
    if not _is_nan(p):
        key = "cfa.report.chi2_good" if p >= 0.05 else "cfa.report.chi2_poor"
        text += t(key, df=df, chi2=_fmt(chi2, 2), p=format_p_apa_full(p))
    text += t(
        "cfa.report.indices",
        rmsea=_fmt(fit["RMSEA"]),
        rmsea_label=_label("RMSEA", fit["RMSEA"]),
        cfi=_fmt(fit["CFI"]),
        cfi_label=_label("CFI", fit["CFI"]),
        tli=_fmt(fit["TLI"]),
        tli_label=_label("TLI", fit["TLI"]),
        srmr=_fmt(fit["SRMR"]),
        srmr_label=_label("SRMR", fit["SRMR"]),
    )
    return text


@log_function
def recalculate_cfa_study(elements, result: CFAResult, update) -> CFAResult:
    """Validate the user's factor structure, fit the CFA by ML, and report fit indices,
    standardised loadings (+ heatmap) and, for oblique models, factor correlations.
    Unexpected exceptions are handled centrally by the panel's recalculate()."""
    cfg: CFAStudyConfig = result.config
    result.result_elements = []

    structure = cfg.column_selector or []
    # Identification: every factor needs at least two assigned variables.
    if not structure or any(len(factor_vars) < 2 for factor_vars in structure):
        return _fail(result, t("cfa.error.min_per_factor"))

    n_factors = len(structure)
    all_vars = [var for factor_vars in structure for var in factor_vars]
    unique_vars = list(dict.fromkeys(all_vars))  # a variable may cross-load on >1 factor

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    # Ordinal items are scored numerically so Likert scales are usable.
    df = data.get_dataframe(columns=unique_vars, map_ordinal=True)
    df = df.select_dtypes(include=[np.number]).astype(float).dropna(axis=0)
    if df.shape[1] < 2 or any(len([v for v in fv if v in df.columns]) < 2 for fv in structure):
        return _fail(result, t("cfa.error.min_per_factor"))

    verbal = bool(cfg.verbal_indicators)
    columns = list(df.columns)
    factor_names = [f"F{i + 1}" for i in range(n_factors)]
    numbering = ColumnNumbering(columns, enabled=bool(cfg.number_columns))

    update(15)
    estimator = CFAEstimator(structure=structure, allow_factor_correlation=cfg.allow_factor_correlation)
    try:
        cfa_result = estimator.fit(df.values, var_names=columns)
    except Exception as e:  # surfaced as a clean validation message
        return _fail(result, t("cfa.error.fit_failed", error=str(e)))
    update(75)

    loadings = cfa_result.std_loadings_
    phi = cfa_result.phi_
    fit = cfa_result.fit_indices_

    # ----- Model fit indices table + prose -----
    fit_table = HTMLTableV2(table_caption=t("cfa.caption.fit"))
    fit_header = [Cell(t("cfa.col.index")), Cell(t("cfa.col.value"), center=True)]
    if verbal:
        fit_header.append(Cell(t("cfa.col.interpretation"), center=True))
    fit_table.add_title_row_apa(Row(fit_header))

    rows = [
        ("χ²", _fmt(fit["Chi-square"], 2), None),
        ("df", "—" if _is_nan(fit["df"]) else str(int(fit["df"])), None),
        (t("common.p_value"), format_p_apa_exact(fit["p-value"]), _interpretation_key("p", fit["p-value"])),
        ("RMSEA", _fmt(fit["RMSEA"]), _interpretation_key("RMSEA", fit["RMSEA"])),
        ("CFI", _fmt(fit["CFI"]), _interpretation_key("CFI", fit["CFI"])),
        ("TLI", _fmt(fit["TLI"]), _interpretation_key("TLI", fit["TLI"])),
        ("SRMR", _fmt(fit["SRMR"]), _interpretation_key("SRMR", fit["SRMR"])),
    ]
    for label, value_str, interp_key in rows:
        cells = [Cell(label, push_to_left=True), Cell(value_str, center=True)]
        if verbal:
            cells.append(Cell(t(f"cfa.fit.{interp_key}") if interp_key else "—", center=True))
        fit_table.add_single_row_apa(Row(cells))
    fit_table.add_text(_fit_prose(fit, cfa_result.converged_))
    result.update_and_add_element(fit_table, "cfa fit")

    # ----- Standardized factor loadings table (with significance stars when verbal) -----
    raw_loadings = cfa_result.loadings_
    loading_se = cfa_result.loading_se_
    load_table = HTMLTableV2(table_caption=t("cfa.caption.loadings"))
    load_table.add_title_row_apa(
        Row([Cell(t("cfa.col.variable"))] + [Cell(name, center=True) for name in factor_names])
    )
    any_stars = False
    for idx, var in enumerate(columns):
        cells = [Cell(numbering.label(var), push_to_left=True)]
        for j in range(n_factors):
            text = format_r_apa(loadings[idx, j])
            if verbal and loading_se is not None:
                se = loading_se[idx, j]
                if not _is_nan(se) and se > 0:
                    z = raw_loadings[idx, j] / se
                    stars = get_stars(2.0 * norm.sf(abs(z)))
                    text += stars
                    any_stars = any_stars or bool(stars)
            cells.append(Cell(text, center=True))
        load_table.add_single_row_apa(Row(cells))
    if verbal and any_stars:
        load_table.add_text(t("cfa.loadings_sig_note"))
    load_table.table_note = numbering.append_to_note(load_table.table_note or "")
    result.update_and_add_element(load_table, "cfa loadings")

    # ----- Loadings heatmap -----
    if cfg.plots:
        loadings_df = pd.DataFrame(loadings, index=columns, columns=factor_names)
        result.update_and_add_element(
            PlotV2(
                items=[Heatmap(df=loadings_df, p=None, label=t("cfa.plot.loadings"))],
                title=t("cfa.plot.loadings"),
                plot_title=t("cfa.plot.loadings"),
                x_axis_title=t("cfa.plot.factors"),
                y_axis_title=t("cfa.plot.variables"),
            ),
            "cfa loadings heatmap",
        )

    # ----- Factor correlations (oblique only) -----
    if cfg.allow_factor_correlation and n_factors > 1:
        phi_table = HTMLTableV2(table_caption=t("cfa.caption.phi"))
        phi_table.add_title_row_apa(Row([Cell()] + [Cell(name, center=True) for name in factor_names]))
        for i in range(n_factors):
            phi_table.add_single_row_apa(
                Row([Cell(factor_names[i], push_to_left=True)] + [Cell(format_r_apa(phi[i, j]), center=True) for j in range(n_factors)])
            )
        result.update_and_add_element(phi_table, "cfa phi")

    result.title_context = f"{n_factors} factors"
    update(100)
    return result
