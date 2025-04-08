#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

import pandas as pd
from scipy import stats

from src.common.decorators import log_function
from src.common.result.classes.html_result import Cell, HTMLTableV2, Row
from src.common.utility import format_p_apa, format_p_apa_full, format_p_gost_full, format_statistic_apa
from src.data_panel.data import Data
from src.modules.contingency.result import ContingencyResult


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

    table = HTMLTableV2(table_caption=f"Contingency Table between {cfg.selected_column1} and {cfg.selected_column2}")

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
    table.add_title_row_apa(
        Row([Cell(cfg.selected_column1)] + [Cell(c) for c in contingency_table.columns] + [Cell("Total")])
    )

    for index, row in contingency_table.iterrows():
        table.add_single_row_apa(Row([Cell(str(index))] + [Cell(c) for c in row] + [Cell(row.sum())]))

    table.add_single_row_apa(
        Row([Cell("Total")] + [Cell(c) for c in contingency_table.sum()] + [Cell(contingency_table.sum().sum())])
    )

    # calculate chi-square test
    chi2, p, dof, expected = stats.chi2_contingency(contingency_table)

    chi2_table = HTMLTableV2(table_caption=f"Chi-square Test between {cfg.selected_column1} and {cfg.selected_column2}")
    chi2_table.add_title_row_apa(Row([Cell("&chi;<sup>2</sup>"), Cell("N"), Cell("df"), Cell("p-value")]))
    chi2_table.add_single_row_apa(
        Row([Cell(chi2), Cell(contingency_table.sum().sum()), Cell(dof), Cell(format_p_apa(p))])
    )

    if p < 0.05:
        chi2_text = (
            f"A significant association was found between {cfg.selected_column1} and "
            f"{cfg.selected_column2} (&chi;<sup>2</sup> = {chi2:.2f}, {format_p_apa_full(p)})."
        )
        chi2_text_ua = (
            f"Знайдено статистично значущу асоціацію між {cfg.selected_column1} та "
            f"{cfg.selected_column2} (&chi;<sup>2</sup> = {chi2:.2f}, {format_p_gost_full(p)})."
        )
    else:
        chi2_text = (
            f"No significant association was found between {cfg.selected_column1} and "
            f"{cfg.selected_column2} (&chi;<sup>2</sup> = {chi2:.2f}, {format_p_apa_full(p)})."
        )
        chi2_text_ua = (
            f"Не знайдено статистично значущої асоціації між {cfg.selected_column1} та "
            f"{cfg.selected_column2} (&chi;<sup>2</sup> = {chi2:.2f}, {format_p_gost_full(p)})."
        )

    chi2_table.add_text(chi2_text + "<br>" + chi2_text_ua)

    # Phi coefficient and Cramer's V
    n = contingency_table.sum().sum()
    phi = (chi2 / n) ** 0.5
    cramer_v = (phi / (min(contingency_table.shape) - 1)) ** 0.5

    phi_table = HTMLTableV2(table_caption="Phi coefficient and Cramer's V")
    phi_table.add_title_row_apa(Row([Cell("Phi coefficient"), Cell("Cramer's V")]))
    phi_table.add_single_row_apa(Row([Cell(format_statistic_apa(phi)), Cell(format_statistic_apa(cramer_v))]))

    if cramer_v < 0.2:
        interpretation = "negligible association"
        interpretation_ua = "нехтовну асоціацію"
    elif cramer_v < 0.3:
        interpretation = "weak association"
        interpretation_ua = "слабку асоціацію"
    elif cramer_v < 0.5:
        interpretation = "moderate association"
        interpretation_ua = "помірну асоціацію"
    else:
        interpretation = "strong association"
        interpretation_ua = "сильну асоціацію"

    phi_table.add_text(
        f"The Cramer's V = {cramer_v:.2f}, indicating {interpretation}."
        + "<br>"
        + f"Значення Cramer's V = {cramer_v:.2f}, що свідчить про {interpretation_ua}."
    )

    result.result_elements = [table, chi2_table, phi_table]
    return result
