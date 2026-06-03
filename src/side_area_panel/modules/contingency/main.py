#  Copyright (c) 2023 StatPrism Team. All rights reserved.


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
from src.side_area_panel.modules.contingency.result import ContingencyResult


@log_function
def recalculate_contingency_study(elements, result: ContingencyResult) -> ContingencyResult:
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    col1 = cfg.column_selector[0][0] if cfg.column_selector[0] else None
    col2 = cfg.column_selector[1][0] if cfg.column_selector[1] else None

    df = data.get_dataframe(
        columns=[col1, col2],
    )

    # calculate contingency table
    contingency_table = pd.crosstab(df[col1], df[col2])

    table = HTMLTableV2(table_caption=t("contingency.table_caption", col1=col1, col2=col2))

    table.add_single_row_apa(
        Row(
            [
                Cell(),
                Cell(
                    col2,
                    col_span=len(contingency_table.columns),
                    border_bottom=True,
                    center=True,
                ),
                Cell(),
            ]
        )
    )

    total_str = t("contingency.total")

    table.add_title_row_apa(
        Row([Cell(col1)] + [Cell(c) for c in contingency_table.columns] + [Cell(total_str)])
    )

    for index, row in contingency_table.iterrows():
        table.add_single_row_apa(Row([Cell(str(index))] + [Cell(c) for c in row] + [Cell(row.sum())]))

    table.add_single_row_apa(
        Row([Cell(total_str)] + [Cell(c) for c in contingency_table.sum()] + [Cell(contingency_table.sum().sum())])
    )

    # calculate chi-square test
    chi2, p, dof, expected = stats.chi2_contingency(contingency_table)
    chi2_no_yates, _, _, _ = stats.chi2_contingency(contingency_table, correction=False)

    # Phi coefficient and Cramer's V
    n = contingency_table.sum().sum()
    phi = (chi2_no_yates / n) ** 0.5  # report only for 2x2 tables
    cramer_v = (chi2_no_yates / n / (min(contingency_table.shape) - 1)) ** 0.5  # valid for any size table

    is_phi_eligible = contingency_table.shape[0] == 2 and contingency_table.shape[1] == 2
    if is_phi_eligible:
        assert phi == cramer_v

    chi2_note = t("contingency.chi2_note")
    if is_phi_eligible:
        chi2_note += ", " + t("contingency.chi2_note_phi")

    chi2_table = HTMLTableV2(
        table_caption=t("contingency.chi2_caption", col1=col1, col2=col2),
        table_note=chi2_note,
    )
    chi2_table.add_title_row_apa(
        Row(
            [
                Cell("&chi;<sup>2</sup>"),
                Cell("N"),
                Cell("df"),
                Cell(t("contingency.col_pvalue")),
                Cell("&phi;" if is_phi_eligible else t("contingency.col_cramer")),
            ]
        )
    )

    chi2_table.add_single_row_apa(
        Row(
            [
                Cell(format_statistic_apa(chi2)),
                Cell(contingency_table.sum().sum()),
                Cell(dof),
                Cell(format_p_apa(p)),
                Cell(format_statistic_apa(cramer_v)),
            ]
        )
    )

    if cramer_v < 0.2:
        interpretation = t("contingency.rel_weak")
    elif cramer_v < 0.6:
        interpretation = t("contingency.rel_moderate")
    else:
        interpretation = t("contingency.rel_strong")

    def format_chi2(chi2_value, p_value, dof):
        return (
            f"&chi;<sup>2</sup>({dof}, N = {contingency_table.sum().sum()}) = {format_statistic_apa(chi2_value)}, "
            f"{format_p_apa_full(p_value)}"
        )

    stats_str = format_chi2(chi2, p, dof)
    if p < 0.05:
        chi2_table_text = t("contingency.significant", col1=col1, col2=col2, stats=stats_str)
    else:
        chi2_table_text = t("contingency.not_significant", col1=col1, col2=col2, stats=stats_str)

    chi2_table_text += t(
        "contingency.cramer_text",
        v=f"{cramer_v:.2f}",
        interpretation=interpretation,
        col1=col1,
        col2=col2,
    )
    chi2_table.add_text(chi2_table_text)

    plot = PlotV2(
        items=[
            ContingencyPlot(
                contingency_table=contingency_table,
                label="Contingency Plot",
            )
        ],
        plot_title=f"Contingency Plot: {col1} vs {col2}",
        x_axis_title=col2,
        y_axis_title=col1 + " (%)",
    )

    result.result_elements = [table, chi2_table, plot]
    return result
