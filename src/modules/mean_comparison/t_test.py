#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

from typing import Dict, Tuple, Union

import pandas as pd
from scipy import stats

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.common.result.classes.html_result import Cell, HTMLResultElement, HTMLTable, HTMLText, Row
from src.common.utility import format_p_apa, format_statistic_apa, get_reasonable_digits
from src.common.verbal.test import describe_test
from src.modules.common.homogeneity import process_homogeneity_check
from src.modules.common.normality import process_normality_check
from src.modules.mean_comparison.constant import MeanComparisonMethod
from src.modules.mean_comparison.result import MeanComparisonResult, MeanComparisonStudyConfig
from src.settings_panel.panels.registry import PanelRegistry


@log_function
def recalculate_mean_comparison_t_test(
    df: pd.DataFrame,
    config: MeanComparisonStudyConfig,
    result: MeanComparisonResult,
    ordinal_orders: Dict[str, Dict[Union[int, float, str], int]],
) -> MeanComparisonResult:
    html_result_element = HTMLResultElement(
        settings_panel_index=PanelRegistry.HTML_RESULT_ITEM_SETTINGS.settings_stacked_widget_index
    )

    numeric_columns = [
        col
        for col, col_type in zip(config.selected_columns, config.selected_columns_types)
        if col_type == ColumnType.NUMERIC
    ]
    non_numeric_columns = [col for col in config.selected_columns if col not in numeric_columns]

    normal_columns, non_normal_columns = [], []
    if config.method in [MeanComparisonMethod.HOMOGENEOUS, MeanComparisonMethod.INHOMOGENEOUS]:
        normal_columns, non_normal_columns = config.selected_columns, []
    elif config.method == MeanComparisonMethod.NON_PARAMETRIC:
        normal_columns, non_normal_columns = [], config.selected_columns
    elif config.method == MeanComparisonMethod.AUTO:
        normal_columns, non_normal_columns, normality_table, normality_text = process_normality_check(
            df=df,
            selected_columns=numeric_columns,
            grouping_column=config.grouping_column,
        )
        if len(numeric_columns) > 0:
            html_result_element.items.append(normality_table)
            html_result_element.items.append(normality_text)

    homogeneous_columns, non_homogeneous_columns = [], []
    if config.method == MeanComparisonMethod.HOMOGENEOUS:
        homogeneous_columns, non_homogeneous_columns = normal_columns, []
    elif config.method == MeanComparisonMethod.INHOMOGENEOUS:
        homogeneous_columns, non_homogeneous_columns = [], normal_columns
    elif config.method == MeanComparisonMethod.AUTO:
        homogeneous_columns, non_homogeneous_columns, homogeneity_table, homogeneity_text = process_homogeneity_check(
            df=df,
            selected_columns=normal_columns,
            grouping_column=config.grouping_column,
        )
        if len(normal_columns) > 0:
            html_result_element.items.append(homogeneity_table)
            html_result_element.items.append(homogeneity_text)

    if len(non_numeric_columns + non_normal_columns) > 0:
        table, text = process_non_normal_t_test(
            df=df,
            non_numeric_columns=non_numeric_columns,
            ordinal_orders=ordinal_orders,
            non_normal_columns=non_normal_columns,
            grouping_column=config.grouping_column,
        )
        html_result_element.items.append(table)
        html_result_element.items.append(text)

    if len(non_homogeneous_columns) > 0:
        table, text = process_non_homogeneous_t_test(
            df=df,
            columns=non_homogeneous_columns,
            grouping_column=config.grouping_column,
        )
        html_result_element.items.append(table)
        html_result_element.items.append(text)

    if len(homogeneous_columns) > 0:
        table, text = process_homogeneous_t_test(
            df=df,
            columns=homogeneous_columns,
            grouping_column=config.grouping_column,
        )
        html_result_element.items.append(table)
        html_result_element.items.append(text)

    result.result_elements = [html_result_element]
    return result


def process_non_normal_t_test(
    df: pd.DataFrame, non_numeric_columns, ordinal_orders, non_normal_columns, grouping_column
) -> Tuple[HTMLTable, HTMLText]:
    table = HTMLTable([])
    table.table_caption = "Mann-Whitney U test"
    table.add_title_row_apa(Row([Cell(), Cell("Mann-Whitney U", center=True), Cell("p-value", center=True)]))
    columns = non_numeric_columns + non_normal_columns

    accepted_columns = []
    rejected_columns = []

    for col in columns:
        group1 = df[df[grouping_column] == df[grouping_column].unique()[0]][col]
        group2 = df[df[grouping_column] == df[grouping_column].unique()[1]][col]

        if col in ordinal_orders:
            ordinal_order = ordinal_orders[col]
            group1 = group1.map(ordinal_order)
            group2 = group2.map(ordinal_order)

        u_stat, p_val = stats.mannwhitneyu(group1, group2)
        if p_val > 0.05:
            accepted_columns.append(col)
        else:
            rejected_columns.append(col)
        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(u_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                ]
            )
        )

    text = HTMLText(
        describe_test(
            test_name="Mann-Whitney U test",
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property="are significantly different",
            no_property="are not significantly different",
        )
    )
    return table, text


def process_homogeneous_t_test(df: pd.DataFrame, columns, grouping_column) -> Tuple[HTMLTable, HTMLText]:
    table = HTMLTable([])
    table.table_caption = "Independent Samples T-test"

    group1_name = df[grouping_column].unique()[0]
    group2_name = df[grouping_column].unique()[1]

    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(group1_name, center=True, col_span=2, border_bottom=True)]
            + [Cell(group2_name, center=True, col_span=2, border_bottom=True)]
            + [Cell(), Cell(), Cell()]
        )
    )

    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell("Mean", center=True),
                Cell("SD", center=True),
                Cell("Mean", center=True),
                Cell("SD", center=True),
                Cell("t-statistic", center=True),
                Cell("p-value", center=True),
                Cell("df", center=True),
            ]
        )
    )

    accepted_columns = []
    rejected_columns = []

    for col in columns:
        digits = get_reasonable_digits(df[col])
        group1 = df[df[grouping_column] == df[grouping_column].unique()[0]][col]
        group2 = df[df[grouping_column] == df[grouping_column].unique()[1]][col]
        t_test_result = stats.ttest_ind(group1, group2)
        t_stat, p_val, deg_free = t_test_result.statistic, t_test_result.pvalue, t_test_result.df
        if p_val > 0.05:
            accepted_columns.append(col)
        else:
            rejected_columns.append(col)
        mean, std = [group.mean() for group in [group1, group2]], [group.std() for group in [group1, group2]]
        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(f"{mean[0]:.{digits}f}", center=True),
                    Cell(f"{std[0]:.{digits}f}", center=True),
                    Cell(f"{mean[1]:.{digits}f}", center=True),
                    Cell(f"{std[1]:.{digits}f}", center=True),
                    Cell(format_statistic_apa(t_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                    Cell(f"{deg_free:.0f}", center=True),
                ]
            )
        )

    text = HTMLText(
        describe_test(
            test_name="Independent Samples T-test",
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property="are significantly different",
            no_property="are not significantly different",
        )
    )
    return table, text


def process_non_homogeneous_t_test(df: pd.DataFrame, columns, grouping_column) -> Tuple[HTMLTable, HTMLText]:
    # inhomogeneous => Welch's t-test
    table = HTMLTable([])
    table.table_caption = "Welch's T-test results"

    group1_name = df[grouping_column].unique()[0]
    group2_name = df[grouping_column].unique()[1]

    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(group1_name, center=True, col_span=2, border_bottom=True)]
            + [Cell(group2_name, center=True, col_span=2, border_bottom=True)]
            + [Cell(), Cell(), Cell()]
        )
    )

    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell("Mean", center=True),
                Cell("SD", center=True),
                Cell("Mean", center=True),
                Cell("SD", center=True),
                Cell("t-statistic", center=True),
                Cell("p-value", center=True),
                Cell("df", center=True),
            ]
        )
    )

    accepted_columns = []
    rejected_columns = []

    for col in columns:
        digits = get_reasonable_digits(df[col])
        group1 = df[df[grouping_column] == df[grouping_column].unique()[0]][col]
        group2 = df[df[grouping_column] == df[grouping_column].unique()[1]][col]
        t_test_result = stats.ttest_ind(group1, group2, equal_var=False)
        t_stat, p_val, deg_free = t_test_result.statistic, t_test_result.pvalue, t_test_result.df
        if p_val > 0.05:
            accepted_columns.append(col)
        else:
            rejected_columns.append(col)

        mean, std = [group.mean() for group in [group1, group2]], [group.std() for group in [group1, group2]]
        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(f"{mean[0]:.{digits}f}", center=True),
                    Cell(f"{std[0]:.{digits}f}", center=True),
                    Cell(f"{mean[1]:.{digits}f}", center=True),
                    Cell(f"{std[1]:.{digits}f}", center=True),
                    Cell(format_statistic_apa(t_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                    Cell(f"{deg_free:.0f}", center=True),
                ]
            )
        )

    text = HTMLText(
        describe_test(
            test_name="Welch's T-test",
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property="are significantly different",
            no_property="are not significantly different",
        )
    )
    return table, text
