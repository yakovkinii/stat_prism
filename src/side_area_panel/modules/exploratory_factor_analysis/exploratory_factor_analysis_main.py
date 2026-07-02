#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging
from typing import Tuple

import numpy as np
import pandas as pd
from factor_analyzer import FactorAnalyzer
from numpy.linalg import inv
from scipy.stats import chi2

from src.common.decorators import log_function
from src.common.qcolor import Colors
from src.common.translations import t
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.column_numbering import ColumnNumbering
from src.side_area_panel.modules.common.mathematics.correlation.correlation import calculate_correlations
from src.side_area_panel.modules.common.prose import prose_enabled
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.result.plot_result import Heatmap, Line, LinePlotConfig, PlotV2, Scatter
from src.side_area_panel.modules.common.utility import (
    format_p_apa_exact,
    format_p_apa_full,
    format_r_apa,
    format_statistic_apa,
    format_value_apa,
)
from src.side_area_panel.modules.correlation.correlation_result import CorrelationType
from src.side_area_panel.modules.exploratory_factor_analysis.exploratory_factor_analysis_result import (
    ExtractionMethod,
    FactorAnalysisResult,
    RotationType,
)

# factor_analyzer rotation strings whose factors are correlated (expose phi_).
_OBLIQUE_ROTATIONS = {"promax", "oblimin", "quartimin", "oblimax", "geomin_obl"}

_ROTATION_MAP = {
    RotationType.VARIMAX: "varimax",
    RotationType.PROMAX: "promax",
    RotationType.OBLIMIN: "oblimin",
    RotationType.OBLIMAX: "oblimax",
    RotationType.QUARTIMIN: "quartimin",
    RotationType.QUARTIMAX: "quartimax",
    RotationType.EQUAMAX: "equamax",
    RotationType.NONE: None,
}
_METHOD_MAP = {
    ExtractionMethod.MINRES: "minres",
    ExtractionMethod.ML: "ml",
    ExtractionMethod.PRINCIPAL: "principal",
}


def _fail(result: FactorAnalysisResult, message: str) -> FactorAnalysisResult:
    """Show a validation message to the user and log it, then stop."""
    logging.warning("EFA: %s", message)
    result.set_error(message)
    return result


def _polychoric_matrix(df) -> np.ndarray:
    """Symmetric polychoric (tetrachoric for binary items) correlation matrix, estimated by the
    in-house pairwise routine and mirrored into a full matrix with a unit diagonal — the same
    construction the Reliability module uses, so the two agree."""
    lower, _, _ = calculate_correlations(df, CorrelationType.POLYCHORIC)
    arr = lower.to_numpy(dtype=float)
    arr = np.where(np.isnan(arr), arr.T, arr)  # mirror the filled lower triangle
    np.fill_diagonal(arr, 1.0)
    return arr


def _resolve_factor_names(raw: str, m: int) -> list:
    """Factor labels for the tables/heatmap. Uses the user's comma-separated names where
    given, filling any gap (or a blank entry) with the default ``F1``, ``F2`` … so there is
    always exactly one label per factor. Extra names beyond ``m`` are ignored."""
    provided = [part.strip() for part in (raw or "").split(",")]
    names = []
    for i in range(m):
        custom = provided[i] if i < len(provided) else ""
        names.append(custom if custom else f"F{i + 1}")
    return names


def _kmo_bartlett(R: np.ndarray, n_samples: int) -> Tuple[float, np.ndarray, float, float, int]:
    """Kaiser-Meyer-Olkin sampling adequacy (overall + per-variable MSA) and Bartlett's
    test of sphericity."""
    invR = inv(R)
    partial = -invR / np.sqrt(np.outer(np.diag(invR), np.diag(invR)))
    np.fill_diagonal(partial, 0.0)
    r2 = R**2
    np.fill_diagonal(r2, 0.0)
    p2 = partial**2
    kmo_num = np.sum(r2)
    kmo_den = kmo_num + np.sum(p2)
    kmo_overall = kmo_num / kmo_den if kmo_den != 0 else np.nan
    msa = 1.0 - (np.sum(p2, axis=0) / (np.sum(p2, axis=0) + np.sum(r2, axis=0)))

    p = R.shape[0]
    detR = max(np.linalg.det(R), 1e-16)  # numerical guard
    chi2_stat = -(n_samples - 1 - (2 * p + 5) / 6) * np.log(detR)
    dof = p * (p - 1) // 2
    p_value = 1 - chi2.cdf(chi2_stat, dof)
    return kmo_overall, msa, chi2_stat, p_value, dof


def _kmo_label(kmo: float) -> str:
    if np.isnan(kmo):
        return t("efa.kmo.unacceptable")
    if kmo >= 0.9:
        key = "marvelous"
    elif kmo >= 0.8:
        key = "meritorious"
    elif kmo >= 0.7:
        key = "middling"
    elif kmo >= 0.6:
        key = "mediocre"
    elif kmo >= 0.5:
        key = "miserable"
    else:
        key = "unacceptable"
    return t(f"efa.kmo.{key}")


@log_function
def recalculate_factor_analysis_study(elements, result: FactorAnalysisResult, update) -> FactorAnalysisResult:
    """Validate inputs, then run EFA: sampling-adequacy diagnostics, eigenvalues + scree
    plot, factor loadings (with communalities/uniquenesses) and a loadings heatmap, plus
    factor correlations and a structure matrix for oblique rotations. Unexpected
    exceptions are handled centrally by the panel's recalculate()."""
    cfg = result.config
    result.result_elements = []

    selected = cfg.column_selector[0] if cfg.column_selector else None
    if not selected or len(selected) < 2:
        return _fail(result, t("efa.error.min_variables"))

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    # Ordinal items are scored numerically so Likert scales are usable.
    df = data.get_dataframe(columns=selected, map_ordinal=True)
    df = df.select_dtypes(include=[np.number]).astype(float).dropna(axis=0)
    n_rows, n_cols = df.shape
    if n_rows < 5 or n_cols < 2:
        return _fail(result, t("efa.error.insufficient"))

    m = cfg.n_factors
    if m > n_cols:
        return _fail(result, t("efa.error.too_many_factors", m=m, n=n_cols))

    x = df.values
    columns = list(df.columns)
    factor_names = _resolve_factor_names(getattr(cfg, "factor_names", None), m)
    numbering = ColumnNumbering(columns, enabled=bool(cfg.number_columns))

    # Inter-item correlation drives KMO/Bartlett, the eigenvalues, and (in polychoric mode) the
    # extraction itself. Pearson uses the raw data; Polychoric feeds the in-house matrix.
    is_polychoric = (cfg.correlation_method or "Pearson") == "Polychoric"
    if is_polychoric:
        correlation = _polychoric_matrix(df)
        if not np.all(np.isfinite(correlation)):
            return _fail(result, t("efa.error.polychoric_failed"))
    else:
        correlation = np.corrcoef(x, rowvar=False)

    # ----- Sampling adequacy (KMO + Bartlett) -----
    kmo_overall, msa, bart_chi2, bart_p, bart_df = _kmo_bartlett(correlation, n_rows)

    show_verbal = bool(cfg.verbal_indicators)

    def _diag_row(cells, interpretation):
        # With verbal indicators on, tack a plain-language cell onto the KMO/Bartlett rows.
        return Row(cells + [Cell(interpretation, center=True)]) if show_verbal else Row(cells)

    bart_word = t("verbal.significant") if bart_p < 0.05 else t("verbal.not_significant")
    diag_table = HTMLTableV2(table_caption=t("efa.caption.kmo"))
    diag_table.add_title_row_apa(
        _diag_row([Cell(t("efa.row.kmo")), Cell(format_r_apa(kmo_overall), center=True)], _kmo_label(kmo_overall))
    )
    for name, val in zip(columns, msa):
        diag_table.add_single_row_apa(
            _diag_row(
                [Cell(t("efa.row.msa", name=numbering.label(name))), Cell(format_r_apa(val), center=True)],
                _kmo_label(val),
            )
        )
    diag_table.add_single_row_apa(
        _diag_row([Cell(t("efa.row.bartlett")), Cell(format_statistic_apa(bart_chi2), center=True)], "—")
    )
    diag_table.add_single_row_apa(_diag_row([Cell(t("efa.row.df")), Cell(str(bart_df), center=True)], "—"))
    diag_table.add_single_row_apa(
        _diag_row([Cell(t("common.p_value")), Cell(format_p_apa_exact(bart_p), center=True)], bart_word)
    )
    diag_text = t("efa.report.kmo", label=_kmo_label(kmo_overall), kmo=format_r_apa(kmo_overall))
    bartlett_key = "efa.report.bartlett_sig" if bart_p < 0.05 else "efa.report.bartlett_ns"
    diag_text += t(bartlett_key, df=bart_df, chi2=format_statistic_apa(bart_chi2), p=format_p_apa_full(bart_p))
    if prose_enabled(cfg.interpretation):
        diag_table.add_text(diag_text)
    diag_table.table_note = numbering.append_to_note(diag_table.table_note or "")
    result.update_and_add_element(diag_table, "efa diagnostics")
    update(30)

    # ----- Eigenvalues + scree plot -----
    eigenvalues = np.sort(np.linalg.eigh(correlation)[0])[::-1]
    variance_pct = eigenvalues / np.sum(eigenvalues) * 100.0
    cumulative_pct = np.cumsum(variance_pct)
    n_kaiser = int(np.sum(eigenvalues > 1))

    eig_table = HTMLTableV2(table_caption=t("efa.caption.eigen"))
    eig_table.add_title_row_apa(
        Row(
            [
                Cell(t("efa.col.component")),
                Cell(t("efa.col.eigenvalue"), center=True),
                Cell(t("efa.col.variance_pct"), center=True),
                Cell(t("efa.col.cumulative"), center=True),
            ]
        )
    )
    for i, (ev, pct, cum) in enumerate(zip(eigenvalues, variance_pct, cumulative_pct), 1):
        eig_table.add_single_row_apa(
            Row(
                [
                    Cell(str(i)),
                    Cell(format_statistic_apa(ev), center=True),
                    Cell(format_value_apa(pct, 1), center=True),
                    Cell(format_value_apa(cum, 1), center=True),
                ]
            )
        )
    if prose_enabled(cfg.interpretation):
        eig_table.add_text(t("efa.report.kaiser", n=n_kaiser) if n_kaiser > 0 else t("efa.report.kaiser_none"))
    result.update_and_add_element(eig_table, "efa eigenvalues")

    if cfg.plots:
        colors = Colors()
        component_axis = np.arange(1, len(eigenvalues) + 1)
        scree_color = colors.get_color_list()
        scree_items = [
            Line(
                x=component_axis,
                y=eigenvalues,
                label=t("efa.col.eigenvalue"),
                legend_string=t("efa.col.eigenvalue"),
                config=LinePlotConfig(color=scree_color),
            ),
            Scatter(x=component_axis, y=eigenvalues, label=t("efa.col.eigenvalue")),
            Line(
                x=np.array([1, len(eigenvalues)]),
                y=np.array([1.0, 1.0]),
                label=t("efa.plot.kaiser_line"),
                legend_string=t("efa.plot.kaiser_line"),
                config=LinePlotConfig(color=colors.get_color_list()),
            ),
        ]
        result.update_and_add_element(
            PlotV2(
                items=scree_items,
                title=t("efa.plot.scree"),
                plot_title=t("efa.plot.scree"),
                x_axis_title=t("efa.col.component"),
                y_axis_title=t("efa.col.eigenvalue"),
            ),
            "efa scree",
        )

    # ----- Extraction + rotation -----
    rotation = _ROTATION_MAP.get(RotationType(cfg.rotation), None)
    method = _METHOD_MAP[ExtractionMethod(cfg.method)]
    rotation_kwargs = {"normalize": bool(cfg.kaiser_normalization)}
    # In polychoric mode the extraction runs on the pre-computed correlation matrix (n is not
    # needed for the loadings); otherwise factor_analyzer works from the raw data.
    fa = FactorAnalyzer(
        n_factors=m,
        method=method,
        rotation=rotation,
        use_smc=True,
        is_corr_matrix=is_polychoric,
        rotation_kwargs=rotation_kwargs,
    )
    fa.fit(correlation if is_polychoric else x)
    update(70)
    loadings = fa.loadings_
    is_oblique = rotation in _OBLIQUE_ROTATIONS and getattr(fa, "phi_", None) is not None
    phi = fa.phi_ if is_oblique else np.eye(m)
    communalities = fa.get_communalities()
    uniquenesses = fa.get_uniquenesses()

    # ----- Factor loadings table -----
    load_table = HTMLTableV2(table_caption=t("efa.caption.loadings", rotation=cfg.rotation))
    load_header = (
        [Cell(t("efa.col.variable"))]
        + [Cell(name, center=True) for name in factor_names]
        + [Cell(t("efa.col.communality"), center=True), Cell(t("efa.col.uniqueness"), center=True)]
    )
    load_table.add_title_row_apa(Row(load_header))
    for idx, var in enumerate(columns):
        row = [Cell(numbering.label(var), push_to_left=True)]
        row += [Cell(format_r_apa(loadings[idx, j]), center=True) for j in range(m)]
        row += [
            Cell(format_r_apa(communalities[idx]), center=True),
            Cell(format_r_apa(uniquenesses[idx]), center=True),
        ]
        load_table.add_single_row_apa(Row(row))
    load_table.table_note = numbering.append_to_note(load_table.table_note or "")
    result.update_and_add_element(load_table, "efa loadings")

    # ----- Loadings heatmap -----
    if cfg.plots:
        loadings_df = pd.DataFrame(loadings, index=columns, columns=factor_names)
        result.update_and_add_element(
            PlotV2(
                items=[Heatmap(df=loadings_df, p=None, label=t("efa.plot.loadings"))],
                title=t("efa.plot.loadings"),
                plot_title=t("efa.plot.loadings"),
                x_axis_title=t("efa.plot.factors"),
                y_axis_title=t("efa.plot.variables"),
            ),
            "efa loadings heatmap",
        )

    # ----- Oblique-only: factor correlations + structure matrix -----
    if is_oblique:
        phi_table = HTMLTableV2(table_caption=t("efa.caption.phi"))
        phi_table.add_title_row_apa(Row([Cell()] + [Cell(name, center=True) for name in factor_names]))
        for i in range(m):
            phi_table.add_single_row_apa(
                Row(
                    [Cell(factor_names[i], push_to_left=True)]
                    + [Cell(format_r_apa(phi[i, j]), center=True) for j in range(m)]
                )
            )
        result.update_and_add_element(phi_table, "efa phi")

        structure = loadings @ phi
        struct_table = HTMLTableV2(table_caption=t("efa.caption.structure"))
        struct_table.add_title_row_apa(
            Row([Cell(t("efa.col.variable"))] + [Cell(name, center=True) for name in factor_names])
        )
        for idx, var in enumerate(columns):
            struct_table.add_single_row_apa(
                Row(
                    [Cell(numbering.label(var), push_to_left=True)]
                    + [Cell(format_r_apa(structure[idx, j]), center=True) for j in range(m)]
                )
            )
        struct_table.table_note = numbering.append_to_note(struct_table.table_note or "")
        result.update_and_add_element(struct_table, "efa structure")

    result.title_context = f"{m} factors, {cfg.rotation}"
    update(100)
    return result
