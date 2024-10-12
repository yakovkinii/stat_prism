from typing import Dict, List, Tuple, Union

import pandas as pd
from scipy import stats

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.common.result.classes.html_result import Cell, HTMLResultElement, HTMLTable, HTMLText, Row
from src.common.result.classes.plot_result import PlotResultElement
from src.common.utility import format_p_apa, format_statistic_apa
from src.common.verbal.test import describe_test
from src.modules.common.homogeneity import process_homogeneity_check
from src.modules.common.normality import process_normality_check
from src.modules.mean_comparison.plot import create_mean_comparison_plot
from src.modules.mean_comparison.result import MeanComparisonResult, MeanComparisonStudyConfig
from src.settings_panel.panels.registry import PanelRegistry


@log_function
def recalculate_mean_comparison_anova(
    df: pd.DataFrame,
    config: MeanComparisonStudyConfig,
    result: MeanComparisonResult,
    ordinal_orders: Dict[str, Dict[Union[int, float, str], int]],
) -> MeanComparisonResult:
    html_result_element = HTMLResultElement(
        settings_panel_index=PanelRegistry.HTML_RESULT_ITEM_SETTINGS.settings_stacked_widget_index
    )
    plot_result_elements = []

    numeric_columns = [
        col
        for col, col_type in zip(config.selected_columns, config.selected_columns_types)
        if col_type == ColumnType.NUMERIC
    ]
    non_numeric_columns = [col for col in config.selected_columns if col not in numeric_columns]

    normal_columns, non_normal_columns, normality_table, normality_text = process_normality_check(
        df=df,
        selected_columns=numeric_columns,
        grouping_column=config.grouping_column,
    )

    if len(numeric_columns) > 0:
        html_result_element.items.append(normality_table)
        html_result_element.items.append(normality_text)

    homogeneous_columns, non_homogeneous_columns, homogeneity_table, homogeneity_text = process_homogeneity_check(
        df=df,
        selected_columns=normal_columns,
        grouping_column=config.grouping_column,
    )

    if len(normal_columns) > 0:
        html_result_element.items.append(homogeneity_table)
        html_result_element.items.append(homogeneity_text)

    if len(non_numeric_columns + non_normal_columns) > 0:
        table, text = process_non_normal_anova(
            df=df,
            non_numeric_columns=non_numeric_columns,
            ordinal_orders=ordinal_orders,
            non_normal_columns=non_normal_columns,
            grouping_column=config.grouping_column,
        )

        html_result_element.items.append(table)
        html_result_element.items.append(text)

    if len(non_homogeneous_columns) > 0:
        table, text, plots = process_non_homogeneous_anova(
            df=df,
            columns=non_homogeneous_columns,
            grouping_column=config.grouping_column,
        )
        html_result_element.items.append(table)
        html_result_element.items.append(text)
        plot_result_elements += plots

    if len(homogeneous_columns) > 0:
        table, text, plots = process_homogeneous_anova(
            df=df,
            columns=homogeneous_columns,
            grouping_column=config.grouping_column,
        )
        html_result_element.items.append(table)
        html_result_element.items.append(text)
        plot_result_elements += plots

    result.result_elements = [html_result_element] + plot_result_elements
    return result


def process_non_normal_anova(
    df: pd.DataFrame, non_numeric_columns, ordinal_orders, non_normal_columns, grouping_column
) -> Tuple[HTMLTable, HTMLText]:
    table = HTMLTable([])
    table.table_caption = "Kruskal-Wallis test"
    table.add_title_row_apa(Row([Cell(), Cell("Kruskal-Wallis H", center=True), Cell("p-value", center=True)]))
    columns = non_numeric_columns + non_normal_columns

    accepted_columns = []
    rejected_columns = []

    for col in columns:
        groups = [group[col].dropna() for name, group in df.groupby(grouping_column)]

        if col in ordinal_orders:
            ordinal_order = ordinal_orders[col]
            groups = [group.map(ordinal_order) for group in groups]

        h_stat, p_val = stats.kruskal(*groups)
        if p_val > 0.05:
            accepted_columns.append(col)
        else:
            rejected_columns.append(col)
        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(h_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                ]
            )
        )

    text = HTMLText(
        describe_test(
            test_name="Kruskal-Wallis test",
            accepted_columns=accepted_columns,
            rejected_columns=rejected_columns,
            accepted_property="have equal means",
            rejected_property="do not have equal means",
        )
    )

    return table, text


def process_non_homogeneous_anova(
    df: pd.DataFrame, columns, grouping_column
) -> Tuple[HTMLTable, HTMLText, List[PlotResultElement]]:
    table = HTMLTable([])
    table.table_caption = "Welch's ANOVA results"

    group_names = df[grouping_column].unique()

    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(name, center=True, col_span=2, border_bottom=True) for name in group_names]
            + [Cell(), Cell(), Cell()]
        )
    )

    table.add_title_row_apa(
        Row(
            [
                Cell(),
                *[Cell("Mean", center=True), Cell("SD", center=True)] * len(group_names),
                Cell("Welch's F", center=True),
                Cell("p-value", center=True),
                Cell("df1", center=True),
                Cell("df2", center=True),
            ]
        )
    )

    accepted_columns = []
    rejected_columns = []
    plots = []

    for col in columns:
        group_data = [df[df[grouping_column] == name][col].dropna() for name in group_names]
        f_stat, p_val = stats.f_oneway(*group_data)
        if p_val > 0.05:
            accepted_columns.append(col)
        else:
            rejected_columns.append(col)
        # Degrees of freedom calculation
        n_groups = len(group_names)
        n_total = sum([len(group) for group in group_data])
        df_between = n_groups - 1
        df_within = n_total - n_groups

        group_means = [group.mean() for group in group_data]
        group_stds = [group.std() for group in group_data]

        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    *[
                        _
                        for mean, std in zip(group_means, group_stds)
                        for _ in (Cell(f"{mean:.2f}", center=True), Cell(f"{std:.2f}", center=True))
                    ],
                    Cell(format_statistic_apa(f_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                    Cell(f"{df_between}", center=True),
                    Cell(f"{df_within}", center=True),
                ]
            )
        )
        plots.append(
            create_mean_comparison_plot(
                groups=group_data,
                group_names=group_names,
                column=col,
                grouping_column=grouping_column,
            )
        )

    text = HTMLText(
        describe_test(
            test_name="Welch's ANOVA",
            accepted_columns=accepted_columns,
            rejected_columns=rejected_columns,
            accepted_property="have equal means",
            rejected_property="do not have equal means",
        )
    )
    return table, text, plots


def process_homogeneous_anova(
    df: pd.DataFrame, columns, grouping_column
) -> Tuple[HTMLTable, HTMLText, List[PlotResultElement]]:
    table = HTMLTable([])
    table.table_caption = "One-Way ANOVA results"

    group_names = df[grouping_column].unique()

    # Adding header with group names and overall layout
    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(name, center=True, col_span=2, border_bottom=True) for name in group_names]
            + [Cell(), Cell(), Cell()]
        )
    )

    table.add_title_row_apa(
        Row(
            [
                Cell(),
                *[Cell("Mean", center=True), Cell("SD", center=True)] * len(group_names),
                Cell("F-statistic", center=True),
                Cell("p-value", center=True),
                Cell("df1", center=True),
                Cell("df2", center=True),
            ]
        )
    )
    accepted_columns = []
    rejected_columns = []
    plots = []

    for col in columns:
        group_data = [df[df[grouping_column] == name][col].dropna() for name in group_names]
        f_stat, p_val = stats.f_oneway(*group_data)
        if p_val > 0.05:
            accepted_columns.append(col)
        else:
            rejected_columns.append(col)
        # Degrees of freedom calculation
        n_groups = len(group_names)
        n_total = sum([len(group) for group in group_data])
        df_between = n_groups - 1
        df_within = n_total - n_groups

        group_means = [group.mean() for group in group_data]
        group_stds = [group.std() for group in group_data]

        # Adding the rows with calculated values
        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    *[
                        _
                        for mean, std in zip(group_means, group_stds)
                        for _ in (Cell(f"{mean:.2f}", center=True), Cell(f"{std:.2f}", center=True))
                    ],
                    Cell(format_statistic_apa(f_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                    Cell(f"{df_between}", center=True),
                    Cell(f"{df_within}", center=True),
                ]
            )
        )
        plots.append(
            create_mean_comparison_plot(
                groups=group_data,
                group_names=group_names,
                column=col,
                grouping_column=grouping_column,
            )
        )

    text = HTMLText(
        describe_test(
            test_name="One-Way ANOVA",
            accepted_columns=accepted_columns,
            rejected_columns=rejected_columns,
            accepted_property="have equal means",
            rejected_property="do not have equal means",
        )
    )

    return table, text, plots
