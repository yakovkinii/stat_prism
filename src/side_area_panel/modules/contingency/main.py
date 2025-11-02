#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import pandas as pd
from scipy import stats

from src.common.constant import NDASH
from src.common.decorators import log_function
from src.common.languages import LANGUAGE
from src.data.data import Data
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
def recalculate_contingency_study(data: Data, result: ContingencyResult) -> ContingencyResult:
    # result.update_header()  # TODO implement
    cfg = result.config

    df = data.get_dataframe(
        filters=result.config.filters,
        columns=[
            result.config.selected_column1,
            result.config.selected_column2,
        ],
    )

    # calculate contingency table
    contingency_table = pd.crosstab(df[cfg.selected_column1], df[cfg.selected_column2])

    if LANGUAGE.is_ua():
        table = HTMLTableV2(table_caption=f"Таблиця сполученості між {cfg.selected_column1} та {cfg.selected_column2}")
    else:
        table = HTMLTableV2(
            table_caption=f"Contingency Table between {cfg.selected_column1} and {cfg.selected_column2}"
        )

    table.add_single_row_apa(
        Row(
            [
                Cell(),
                Cell(
                    cfg.selected_column2,
                    col_span=len(contingency_table.columns),
                    border_bottom=True,
                    center=True,
                ),
                Cell(),
            ]
        )
    )

    total_str = "Загалом" if LANGUAGE.is_ua() else "Total"

    table.add_title_row_apa(
        Row([Cell(cfg.selected_column1)] + [Cell(c) for c in contingency_table.columns] + [Cell(total_str)])
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

    if LANGUAGE.is_ua():
        chi2_table = HTMLTableV2(
            table_caption=f"Хі-квадрат тест між {cfg.selected_column1} та {cfg.selected_column2}",
            table_note=(
                f"&chi;<sup>2</sup> {NDASH} статистика хі-квадрат, "
                f"N {NDASH} кількість респондентів, df {NDASH} ступені свободи"
                + f"&phi; {NDASH} коефіцієнт фі" * is_phi_eligible
            ),
        )
        chi2_table.add_title_row_apa(
            Row(
                [
                    Cell("&chi;<sup>2</sup>"),
                    Cell("N"),
                    Cell("df"),
                    Cell("p-значення"),
                    Cell("&phi;" if is_phi_eligible else "V Крамера"),
                ]
            )
        )
    else:
        chi2_table = HTMLTableV2(
            table_caption=f"Chi-square Test between {cfg.selected_column1} and {cfg.selected_column2}"
        )
        chi2_table.add_title_row_apa(
            Row(
                [
                    Cell("&chi;<sup>2</sup>"),
                    Cell("N"),
                    Cell("df"),
                    Cell("p-value"),
                    Cell("&phi;" if is_phi_eligible else "Cramer's V"),
                ],
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
        interpretation = "weak relationship"
        interpretation_ua = "слабкий зв'язок"
    elif cramer_v < 0.6:
        interpretation = "moderate relationship"
        interpretation_ua = "помірний зв'язок"
    else:
        interpretation = "strong relationship"
        interpretation_ua = "сильний зв'язок"

    def format_chi2(chi2_value, p_value, dof):
        return (
            f"&chi;<sup>2</sup>({dof}, N = {contingency_table.sum().sum()}) = {format_statistic_apa(chi2_value)}, "
            f"{format_p_apa_full(p_value)}"
        )

    chi2_table_text = ""

    if p < 0.05:
        if LANGUAGE.is_ua():
            chi2_table_text += (
                f"Знайдено статистично значущий зв'язок між {cfg.selected_column1} та "
                f"{cfg.selected_column2}: {format_chi2(chi2, p, dof)}."
            )
        else:
            chi2_table_text += (
                f"A significant relationship was found between {cfg.selected_column1} and "
                f"{cfg.selected_column2}: {format_chi2(chi2, p, dof)}."
            )
    else:
        if LANGUAGE.is_ua():
            chi2_table_text += (
                f"Не знайдено статистично значущого зв'язку між {cfg.selected_column1} та "
                f"{cfg.selected_column2}: {format_chi2(chi2, p, dof)}."
            )
        else:
            chi2_table_text += (
                f"No significant relationship was found between {cfg.selected_column1} and "
                f"{cfg.selected_column2}: {format_chi2(chi2, p, dof)}."
            )

    if LANGUAGE.is_ua():
        chi2_table_text += (
            f"V Крамера = {cramer_v:.2f}, що свідчить про {interpretation_ua} "
            f"між {cfg.selected_column1} та {cfg.selected_column2}."
        )
    else:
        chi2_table_text += (
            f"The Cramer's V = {cramer_v:.2f}, indicating a {interpretation} "
            f"between {cfg.selected_column1} and {cfg.selected_column2}."
        )
    chi2_table.add_text(chi2_table_text)

    plot = PlotV2(
        items=[
            ContingencyPlot(
                contingency_table=contingency_table,
                label="Contingency Plot",
            )
        ],
        plot_title=f"Contingency Plot: {cfg.selected_column1} vs {cfg.selected_column2}",
        x_axis_title=cfg.selected_column2,
        y_axis_title=cfg.selected_column1 + " (%)",
    )

    result.result_elements = [table, chi2_table, plot]
    return result
