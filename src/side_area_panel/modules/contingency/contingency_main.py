#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

import numpy as np
import pandas as pd
from scipy import stats

from src.common.decorators import log_function
from src.common.translations import t
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.prose import prose_enabled, prose_includes
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.result.plot_result import ContingencyPlot, PlotV2
from src.side_area_panel.modules.common.utility import format_p_apa, format_p_apa_full, format_statistic_apa
from src.side_area_panel.modules.common.verbal.significance import significance_verbal
from src.side_area_panel.modules.contingency.constant import PCT_COLUMN, PCT_NONE, PCT_ROW, PCT_TOTAL
from src.side_area_panel.modules.contingency.contingency_result import ContingencyResult

# Adjusted standardized residual beyond which a cell is flagged (two-tailed, p < .05).
_RESIDUAL_THRESHOLD = 1.96


def _fail(result: ContingencyResult, message: str) -> ContingencyResult:
    """Show a validation message to the user and log it, then stop."""
    logging.warning("Contingency: %s", message)
    result.set_error(message)
    return result


def _build_counts_table(contingency_table: pd.DataFrame, col1: str, col2: str) -> HTMLTableV2:
    """The cross-tabulation of counts with row/column totals."""
    table = HTMLTableV2(table_caption=t("contingency.table_caption", col1=col1, col2=col2))
    total_str = t("contingency.total")

    table.add_single_row_apa(
        Row(
            [
                Cell(),
                Cell(col2, col_span=len(contingency_table.columns), border_bottom=True, center=True),
                Cell(),
            ]
        )
    )
    table.add_title_row_apa(Row([Cell(col1)] + [Cell(c) for c in contingency_table.columns] + [Cell(total_str)]))
    for index, row in contingency_table.iterrows():
        table.add_single_row_apa(Row([Cell(str(index))] + [Cell(c) for c in row] + [Cell(row.sum())]))
    table.add_single_row_apa(
        Row([Cell(total_str)] + [Cell(c) for c in contingency_table.sum()] + [Cell(contingency_table.sum().sum())])
    )
    return table


def _build_percent_table(contingency_table: pd.DataFrame, col1: str, col2: str, mode: str) -> HTMLTableV2:
    """Percentages of the counts, normalised by row, column or grand total (SPSS-style).

    The margin cells make the normalisation explicit: a row-% table's right margin is
    100% per row and its bottom margin is each column's overall share, and vice-versa for
    column %; a total-% table's margins are the overall row / column distributions."""
    ct = contingency_table
    n = ct.values.sum()
    row_tot = ct.sum(axis=1)
    col_tot = ct.sum(axis=0)

    if mode == PCT_ROW:
        inner = ct.div(row_tot, axis=0) * 100
        right_margin = pd.Series(100.0, index=ct.index)
        bottom_margin = col_tot / n * 100
        note_key = "contingency.pct_note_row"
    elif mode == PCT_COLUMN:
        inner = ct.div(col_tot, axis=1) * 100
        right_margin = row_tot / n * 100
        bottom_margin = pd.Series(100.0, index=ct.columns)
        note_key = "contingency.pct_note_column"
    else:  # PCT_TOTAL
        inner = ct / n * 100
        right_margin = row_tot / n * 100
        bottom_margin = col_tot / n * 100
        note_key = "contingency.pct_note_total"

    def pct(value) -> str:
        return f"{value:.1f}%"

    table = HTMLTableV2(
        table_caption=t("contingency.pct_caption", col1=col1, col2=col2),
        table_note=t(note_key),
    )
    total_str = t("contingency.total")
    table.add_single_row_apa(
        Row([Cell(), Cell(col2, col_span=len(ct.columns), border_bottom=True, center=True), Cell()])
    )
    table.add_title_row_apa(Row([Cell(col1)] + [Cell(c) for c in ct.columns] + [Cell(total_str)]))
    for index, row in inner.iterrows():
        cells = [Cell(str(index))] + [Cell(pct(v)) for v in row] + [Cell(pct(right_margin.loc[index]))]
        table.add_single_row_apa(Row(cells))
    bottom = [Cell(total_str)] + [Cell(pct(bottom_margin.loc[c])) for c in ct.columns] + [Cell(pct(100.0))]
    table.add_single_row_apa(Row(bottom))
    return table


def _build_residuals_table(contingency_table: pd.DataFrame, expected, col1: str, col2: str) -> HTMLTableV2:
    """Adjusted standardized residuals (Agresti/Haberman) for each cell. Cells whose
    |residual| exceeds ~1.96 (bold) drive the significant association — a simple post-hoc
    locating *where* the two variables depart from independence."""
    ct = contingency_table
    observed = ct.to_numpy(dtype=float)
    expected = np.asarray(expected, dtype=float)
    n = observed.sum()
    row_frac = observed.sum(axis=1, keepdims=True) / n
    col_frac = observed.sum(axis=0, keepdims=True) / n
    denom = np.sqrt(expected * (1 - row_frac) * (1 - col_frac))
    with np.errstate(divide="ignore", invalid="ignore"):
        adjusted = np.where(denom > 0, (observed - expected) / denom, 0.0)

    table = HTMLTableV2(
        table_caption=t("contingency.residuals.caption", col1=col1, col2=col2),
        table_note=t("contingency.residuals.note", z=f"{_RESIDUAL_THRESHOLD:.2f}"),
    )
    table.add_single_row_apa(Row([Cell(), Cell(col2, col_span=len(ct.columns), border_bottom=True, center=True)]))
    table.add_title_row_apa(Row([Cell(col1)] + [Cell(c) for c in ct.columns]))
    for i, index in enumerate(ct.index):
        cells = [Cell(str(index))]
        for j in range(len(ct.columns)):
            value = adjusted[i, j]
            flagged = abs(value) > _RESIDUAL_THRESHOLD
            cells.append(Cell(format_statistic_apa(value), is_bold=flagged))
        table.add_single_row_apa(Row(cells))
    return table


def _add_mcnemar_table(result, contingency_table, correction, prose_detail):
    """Paired-data symmetry test on a square table: McNemar for 2x2, its Bowker
    generalisation for larger square tables. Skips (with a note) when the table is not
    square, since the two variables must share the same categories (matched conditions)."""
    from statsmodels.stats.contingency_tables import SquareTable, mcnemar

    table = HTMLTableV2(table_caption=t("contingency.mcnemar.caption"))
    if contingency_table.shape[0] != contingency_table.shape[1] or list(contingency_table.index) != list(
        contingency_table.columns
    ):
        table.add_text(t("contingency.mcnemar.not_square"))
        result.update_and_add_element(table, "contingency mcnemar")
        return

    arr = contingency_table.to_numpy()
    if contingency_table.shape == (2, 2):
        n_discordant = int(arr[0, 1] + arr[1, 0])
        res = mcnemar(arr, exact=(n_discordant < 25), correction=correction)
        stat, p, dof = float(res.statistic), float(res.pvalue), 1
        name = t("contingency.mcnemar.name")
    else:
        res = SquareTable(arr).symmetry()
        stat, p, dof = float(res.statistic), float(res.pvalue), int(res.df)
        name = t("contingency.mcnemar.name_bowker")

    table.add_title_row_apa(Row([Cell("&chi;<sup>2</sup>"), Cell("df"), Cell(t("contingency.col_pvalue"))]))
    table.add_single_row_apa(Row([Cell(format_statistic_apa(stat)), Cell(str(dof)), Cell(format_p_apa(p))]))
    if prose_includes(prose_detail, p < 0.05, p < 0.05):
        key = "contingency.mcnemar.significant" if p < 0.05 else "contingency.mcnemar.not_significant"
        table.add_text(t(key, name=name, stats=f"χ²({dof}) = {format_statistic_apa(stat)}, {format_p_apa_full(p)}"))
    result.update_and_add_element(table, "contingency mcnemar")


@log_function
def recalculate_contingency_study(elements, result: ContingencyResult, update) -> ContingencyResult:
    """Validate the inputs, build the contingency table, run the chi-square test (with an
    effect size and, for small 2x2 tables, Fisher's exact test), and a distribution plot.
    Unexpected exceptions are handled centrally by the panel's recalculate()."""
    cfg = result.config
    result.result_elements = []

    cols1 = cfg.column_selector[0]
    cols2 = cfg.column_selector[1]
    if not cols1 or not cols2:
        return _fail(result, t("contingency.error.select_two"))
    col1, col2 = cols1[0], cols2[0]
    if col1 == col2:
        return _fail(result, t("contingency.error.distinct"))

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    df = data.get_dataframe(columns=[col1, col2])

    contingency_table = pd.crosstab(df[col1], df[col2])
    if contingency_table.empty or contingency_table.values.sum() == 0:
        return _fail(result, t("contingency.error.no_data"))
    if contingency_table.shape[0] < 2 or contingency_table.shape[1] < 2:
        return _fail(result, t("contingency.error.min_categories"))

    # crosstab sorts categories alphabetically; reorder both axes by each column's defined
    # order so ordinal categories follow their ordinality rather than the alphabet.
    contingency_table = contingency_table.reindex(
        index=data.ordered_categories(col1, list(contingency_table.index)),
        columns=data.ordered_categories(col2, list(contingency_table.columns)),
    )

    update(40)
    # ----- Counts table -----
    result.update_and_add_element(_build_counts_table(contingency_table, col1, col2), "contingency counts")

    # ----- Percentages table (row / column / total) -----
    pct_mode = cfg.percentages or PCT_NONE
    if pct_mode in (PCT_ROW, PCT_COLUMN, PCT_TOTAL):
        result.update_and_add_element(
            _build_percent_table(contingency_table, col1, col2, pct_mode), "contingency percentages"
        )

    # ----- Chi-square test -----
    # The continuity-correction toggle is applied consistently to BOTH the chi-square
    # statistic and the effect size (Yates affects 2x2 tables only).
    correction = bool(cfg.continuity_correction)
    chi2, p, dof, expected = stats.chi2_contingency(contingency_table, correction=correction)

    n = contingency_table.sum().sum()
    is_2x2 = contingency_table.shape == (2, 2)
    # phi == Cramer's V for 2x2 (min(r,c) - 1 == 1); one formula covers both.
    cramer_v = (chi2 / n / (min(contingency_table.shape) - 1)) ** 0.5

    show_effect = bool(cfg.effect_size)
    show_verbal = bool(cfg.verbal_indicators)

    # Verbal magnitude of the association, reused by both the table column and the prose.
    if cramer_v < 0.2:
        cramer_interpretation = t("contingency.rel_weak")
    elif cramer_v < 0.6:
        cramer_interpretation = t("contingency.rel_moderate")
    else:
        cramer_interpretation = t("contingency.rel_strong")

    note = t("contingency.chi2_note")
    if show_effect and is_2x2:
        note += ", " + t("contingency.chi2_note_phi")

    chi2_table = HTMLTableV2(
        table_caption=t("contingency.chi2_caption", col1=col1, col2=col2),
        table_note=note,
    )

    header = [
        Cell("&chi;<sup>2</sup>"),
        Cell("N"),
        Cell("df"),
        Cell(t("contingency.col_pvalue")),
    ]
    values = [
        Cell(format_statistic_apa(chi2)),
        Cell(n),
        Cell(dof),
        Cell(format_p_apa(p)),
    ]
    if show_verbal:
        header.append(Cell(t("verbal.col_significant")))
        values.append(Cell(significance_verbal(p)))
    if show_effect:
        header.append(Cell("&phi;" if is_2x2 else t("contingency.col_cramer")))
        values.append(Cell(format_statistic_apa(cramer_v)))
        if show_verbal:
            header.append(Cell(t("effect.col.magnitude")))
            values.append(Cell(cramer_interpretation))
    chi2_table.add_title_row_apa(Row(header))
    chi2_table.add_single_row_apa(Row(values))

    # Written interpretation follows the "Verbal report" dropdown: at Full it is always shown,
    # at the compact levels only when the association is significant.
    if prose_includes(cfg.interpretation, p < 0.05, p < 0.05):
        stats_str = f"&chi;<sup>2</sup>({dof}, N = {n}) = {format_statistic_apa(chi2)}, {format_p_apa_full(p)}"
        if p < 0.05:
            chi2_text = t("contingency.significant", col1=col1, col2=col2, stats=stats_str)
        else:
            chi2_text = t("contingency.not_significant", col1=col1, col2=col2, stats=stats_str)

        if show_effect:
            effect_name = "&phi;" if is_2x2 else t("contingency.col_cramer")
            chi2_text += " " + t(
                "contingency.cramer_text",
                name=effect_name,
                v=f"{cramer_v:.2f}",
                interpretation=cramer_interpretation,
                col1=col1,
                col2=col2,
            )
        chi2_table.add_text(chi2_text)

    # For 2x2 tables that violate the expected-count assumption, report Fisher's exact
    # test instead (the assumption itself is documented in the method's fine-print).
    low_expected_count = int((expected < 5).sum())
    if is_2x2 and low_expected_count > 0 and prose_enabled(cfg.interpretation):
        odds_ratio, fisher_p = stats.fisher_exact(contingency_table.to_numpy())
        chi2_table.add_text(
            t(
                "contingency.fisher_text",
                odds=format_statistic_apa(odds_ratio),
                p=format_p_apa_full(fisher_p),
            )
        )

    result.update_and_add_element(chi2_table, "contingency chi2")

    # ----- Post-hoc adjusted standardized residuals (only when the omnibus is significant) -----
    if cfg.post_hoc:
        if p < 0.05:
            result.update_and_add_element(
                _build_residuals_table(contingency_table, expected, col1, col2), "contingency residuals"
            )
        else:
            chi2_table.add_text(t("contingency.residuals.not_significant"))

    # ----- Symmetry test for paired data (McNemar 2x2 / Bowker larger) -----
    if cfg.mcnemar:
        _add_mcnemar_table(result, contingency_table, correction, cfg.interpretation)

    update(70)

    # ----- Plot -----
    if cfg.plots:
        plot = PlotV2(
            items=[ContingencyPlot(contingency_table=contingency_table, label="Contingency Plot")],
            plot_title=t("contingency.plot_title", col1=col1, col2=col2),
            x_axis_title=col2,
            y_axis_title=t("contingency.plot_y_axis", col=col1),
        )
        result.update_and_add_element(plot, "contingency plot")

    result.title_context = f"{str(col1)[:16]} × {str(col2)[:16]}"
    update(100)
    return result
