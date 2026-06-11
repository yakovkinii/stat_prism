#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

import pandas as pd
from scipy import stats

from src.common.decorators import log_function
from src.common.translations import t
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.result.plot_result import (
    ContingencyPlot,
    PlotV2,
)
from src.side_area_panel.modules.common.utility import (
    format_p_apa,
    format_p_apa_full,
    format_statistic_apa,
)
from src.side_area_panel.modules.common.verbal.significance import significance_verbal
from src.side_area_panel.modules.contingency.contingency_result import ContingencyResult


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
    table.add_title_row_apa(
        Row([Cell(col1)] + [Cell(c) for c in contingency_table.columns] + [Cell(total_str)])
    )
    for index, row in contingency_table.iterrows():
        table.add_single_row_apa(Row([Cell(str(index))] + [Cell(c) for c in row] + [Cell(row.sum())]))
    table.add_single_row_apa(
        Row([Cell(total_str)] + [Cell(c) for c in contingency_table.sum()] + [Cell(contingency_table.sum().sum())])
    )
    return table


@log_function
def recalculate_contingency_study(elements, result: ContingencyResult) -> ContingencyResult:
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

    # ----- Counts table -----
    result.update_and_add_element(_build_counts_table(contingency_table, col1, col2), "contingency counts")

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

    stats_str = (
        f"&chi;<sup>2</sup>({dof}, N = {n}) = {format_statistic_apa(chi2)}, {format_p_apa_full(p)}"
    )
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
    if is_2x2 and low_expected_count > 0:
        odds_ratio, fisher_p = stats.fisher_exact(contingency_table.to_numpy())
        chi2_table.add_text(
            t(
                "contingency.fisher_text",
                odds=format_statistic_apa(odds_ratio),
                p=format_p_apa_full(fisher_p),
            )
        )

    result.update_and_add_element(chi2_table, "contingency chi2")

    # ----- Plot -----
    if cfg.plots:
        plot = PlotV2(
            items=[ContingencyPlot(contingency_table=contingency_table, label="Contingency Plot")],
            plot_title=t("contingency.plot_title", col1=col1, col2=col2),
            x_axis_title=col2,
            y_axis_title=t("contingency.plot_y_axis", col=col1),
        )
        result.update_and_add_element(plot, "contingency plot")

    return result
