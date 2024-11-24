#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

from typing import Dict, Union

import pandas as pd
import pingouin as pg
from scikit_posthocs import posthoc_dunn, posthoc_tamhane, posthoc_tukey_hsd
from scipy import stats

from src.common.constant import MDASH, ColumnType
from src.common.decorators import log_function
from src.common.result.classes.html_result import Cell, HTMLResultElement, HTMLTable, HTMLText, Row
from src.common.utility import format_p_apa, format_p_apa_full, format_statistic_apa, format_value_apa, smart_comma_join
from src.common.verbal.test import TestResult, describe_single_test_multiple_variables
from src.modules.common.homogeneity import process_homogeneity_check
from src.modules.common.normality import process_normality_check
from src.modules.mean_comparison.constant import MeanComparisonMethod
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
        items = process_non_normal_anova(
            df=df,
            non_numeric_columns=non_numeric_columns,
            ordinal_orders=ordinal_orders,
            non_normal_columns=non_normal_columns,
            grouping_column=config.grouping_column,
            means=config.means,
            effect_size=config.effect_size,
        )
        for item in items:
            html_result_element.items.append(item)

    if len(non_homogeneous_columns) > 0:
        items = process_non_homogeneous_anova(
            df=df,
            columns=non_homogeneous_columns,
            grouping_column=config.grouping_column,
            means=config.means,
            effect_size=config.effect_size,
        )
        for item in items:
            html_result_element.items.append(item)

    if len(homogeneous_columns) > 0:
        items = process_homogeneous_anova(
            df=df,
            columns=homogeneous_columns,
            grouping_column=config.grouping_column,
            means=config.means,
            effect_size=config.effect_size,
        )
        for item in items:
            html_result_element.items.append(item)

    result.result_elements = [html_result_element]
    return result


def process_non_normal_anova(
    df: pd.DataFrame, non_numeric_columns, ordinal_orders, non_normal_columns, grouping_column, means, effect_size
):
    table = HTMLTable([])
    table.table_caption = "Kruskal-Wallis test"

    group_names = df[grouping_column].unique().tolist()

    table.add_single_row_apa(
        Row([Cell()] * 4 + [Cell(name, center=True, col_span=2, border_bottom=True) for name in group_names])
    )

    table.add_title_row_apa(
        Row(
            [Cell(), Cell("Kruskal-Wallis H", center=True), Cell("p-value", center=True), Cell("df", center=True)]
            + [Cell("Median", center=True), Cell("IQR", center=True)] * len(group_names) * means
        )
    )

    columns = non_numeric_columns + non_normal_columns

    accepted_columns = []
    rejected_columns = []
    subgroup_results = {}
    significant_columns = []

    for col in columns:
        groups = [group[col].dropna() for name, group in df.groupby(grouping_column)]

        if col in ordinal_orders:
            ordinal_order = ordinal_orders[col]
            groups = [group.map(ordinal_order) for group in groups]

        h_stat, p_val = stats.kruskal(*groups)

        median = [group.median() for group in groups]
        iqr = [group.quantile(0.75) - group.quantile(0.25) for group in groups]

        if p_val > 0.05:
            accepted_columns.append(TestResult(variable=col, letter="H", statistic=h_stat, p=p_val))
        else:
            rejected_columns.append(TestResult(variable=col, letter="H", statistic=h_stat, p=p_val))
            significant_columns.append(col)

        subgroup_results[col] = [
            TestResult(variable=group_name, letter=["Median", "IQR"], statistic=[median[i], iqr[i]], decimals=1)
            for i, group_name in enumerate(group_names)
        ]

        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(h_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                    Cell(str(len(groups) - 1), center=True),
                ]
                + [
                    _
                    for median_value, iqr_value in zip(median, iqr)
                    for _ in (
                        Cell(format_value_apa(median_value), center=True),
                        Cell(format_value_apa(iqr_value), center=True),
                    )
                ]
                * means
            )
        )

    text = HTMLText(
        describe_single_test_multiple_variables(
            test_name="Kruskal-Wallis test",
            test_check="difference between groups",
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property="are significantly different across the groups",
            no_property="are not significantly different across the groups",
            subgroup_results=subgroup_results if means else None,
        )
    )

    if not effect_size:
        return table, text

    post_hoc_items = []

    for col in significant_columns:
        significant = []
        posthoc_table = HTMLTable([])
        posthoc_table.table_caption = "Dunn's post-hoc test results"
        posthoc_table.add_single_row_apa(
            Row([Cell()] + [Cell("p-value", col_span=len(group_names), center=True, border_bottom=True)])
        )
        posthoc_table.add_title_row_apa(Row([Cell()] + [Cell(name, center=True) for name in group_names]))
        posthoc_results = posthoc_dunn(df, val_col=col, group_col=grouping_column)
        for i, group_name in enumerate(group_names):
            row = [Cell(group_name, push_to_left=True)]
            for j in range(i + 1):
                if i == j:
                    row.append(Cell(MDASH, center=True))
                else:
                    row.append(Cell(format_p_apa(posthoc_results.iloc[i, j]), center=True))
                    if posthoc_results.iloc[i, j] < 0.05:
                        significant.append((i, j))
            posthoc_table.add_single_row_apa(Row(row))

        post_hoc_items.append(posthoc_table)

        post_hoc_items.append(
            HTMLText(
                f"The Dunn's post-hoc test for {col} has revealed a "
                f"significant difference between the following groups: "
                + smart_comma_join(
                    [
                        f"{group_names[i]} and {group_names[j]} ({format_p_apa_full(posthoc_results.iloc[i,j])})"
                        for i, j in significant
                    ]
                )
                + "."
            )
        )

    return table, text, *post_hoc_items


def process_non_homogeneous_anova(df: pd.DataFrame, columns, grouping_column, means, effect_size):
    table = HTMLTable([])
    table.table_caption = "Welch's ANOVA results"

    group_names = df[grouping_column].unique()

    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(), Cell(), Cell(), Cell()]
            + [Cell(name, center=True, col_span=2, border_bottom=True) for name in group_names]
        )
    )

    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell("Welch's F", center=True),
                Cell("p-value", center=True),
                Cell("df1", center=True),
                Cell("df2", center=True),
                *[Cell("Mean", center=True), Cell("SD", center=True)] * len(group_names),
            ]
        )
    )

    accepted_columns = []
    rejected_columns = []
    subgroup_results = {}
    significant_columns = []

    for col in columns:
        group_data = [df[df[grouping_column] == name][col].dropna() for name in group_names]
        welch_result = pg.welch_anova(data=df, dv=col, between=grouping_column)

        f_stat = welch_result["F"].values[0]
        p_val = welch_result["p-unc"].values[0]
        df_between = welch_result["ddof1"].values[0]
        df_within = f"{welch_result['ddof2'].values[0]:.1f}"

        if p_val > 0.05:
            accepted_columns.append(
                TestResult(variable=col, letter="F", statistic=f_stat, p=p_val, df=df_between, df2=df_within)
            )
        else:
            rejected_columns.append(
                TestResult(variable=col, letter="F", statistic=f_stat, p=p_val, df=df_between, df2=df_within)
            )
            significant_columns.append(col)

        group_means = [group.mean() for group in group_data]
        group_stds = [group.std() for group in group_data]

        subgroup_results[col] = [
            TestResult(
                variable=group_name, letter=["Mean", "SD"], statistic=[group_means[i], group_stds[i]], decimals=1
            )
            for i, group_name in enumerate(group_names)
        ]

        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(f_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                    Cell(f"{df_between}", center=True),
                    Cell(f"{df_within}", center=True),
                    *[
                        _
                        for mean, std in zip(group_means, group_stds)
                        for _ in (Cell(format_value_apa(mean), center=True), Cell(format_value_apa(std), center=True))
                    ],
                ]
            )
        )

    text = HTMLText(
        describe_single_test_multiple_variables(
            test_name="Welch's ANOVA",
            test_check="equality of means",
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property="have different means",
            no_property="have equal means",
            subgroup_results=subgroup_results,
        )
    )

    if not effect_size:
        return table, text

    post_hoc_items = []

    for col in significant_columns:
        significant = []
        posthoc_table = HTMLTable([])
        posthoc_table.table_caption = "Tamhane's T2 post-hoc test results"
        posthoc_table.add_single_row_apa(
            Row([Cell()] + [Cell("p-value", col_span=len(group_names), center=True, border_bottom=True)])
        )
        posthoc_table.add_title_row_apa(Row([Cell()] + [Cell(name, center=True) for name in group_names]))
        posthoc_results = posthoc_tamhane(df, val_col=col, group_col=grouping_column)

        for i, group_name in enumerate(group_names):
            row = [Cell(group_name, push_to_left=True)]
            for j in range(i + 1):
                if i == j:
                    row.append(Cell(MDASH, center=True))
                else:
                    row.append(Cell(format_p_apa(posthoc_results.iloc[i, j]), center=True))
                    if posthoc_results.iloc[i, j] < 0.05:
                        significant.append((i, j))
            posthoc_table.add_single_row_apa(Row(row))

        post_hoc_items.append(posthoc_table)

        post_hoc_items.append(
            HTMLText(
                f"The Tamhane's T2 post-hoc test for {col} has revealed a "
                f"significant difference between the following groups: "
                + smart_comma_join(
                    [
                        f"{group_names[i]} and {group_names[j]} ({format_p_apa_full(posthoc_results.iloc[i, j])})"
                        for i, j in significant
                    ]
                )
                + "."
            )
        )

    return table, text, *post_hoc_items


def process_homogeneous_anova(df: pd.DataFrame, columns, grouping_column, means, effect_size):
    table = HTMLTable([])
    table.table_caption = "One-Way ANOVA results"

    group_names = df[grouping_column].unique()

    # Adding header with group names and overall layout
    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(), Cell(), Cell(), Cell()]
            + [Cell(name, center=True, col_span=2, border_bottom=True) for name in group_names]
        )
    )

    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell("F-statistic", center=True),
                Cell("p-value", center=True),
                Cell("df1", center=True),
                Cell("df2", center=True),
                *[Cell("Mean", center=True), Cell("SD", center=True)] * len(group_names),
            ]
        )
    )
    accepted_columns = []
    rejected_columns = []
    subgroup_results = {}
    significant_columns = []

    for col in columns:
        group_data = [df[df[grouping_column] == name][col].dropna() for name in group_names]
        f_stat, p_val = stats.f_oneway(*group_data)

        # Degrees of freedom calculation
        n_groups = len(group_names)
        n_total = sum([len(group) for group in group_data])
        df_between = n_groups - 1
        df_within = n_total - n_groups

        if p_val > 0.05:
            accepted_columns.append(
                TestResult(variable=col, letter="F", statistic=f_stat, p=p_val, df=df_between, df2=df_within)
            )
        else:
            rejected_columns.append(
                TestResult(variable=col, letter="F", statistic=f_stat, p=p_val, df=df_between, df2=df_within)
            )
            significant_columns.append(col)

        group_means = [group.mean() for group in group_data]
        group_stds = [group.std() for group in group_data]

        subgroup_results[col] = [
            TestResult(
                variable=group_name, letter=["Mean", "SD"], statistic=[group_means[i], group_stds[i]], decimals=1
            )
            for i, group_name in enumerate(group_names)
        ]

        # Adding the rows with calculated values
        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(f_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                    Cell(f"{df_between}", center=True),
                    Cell(f"{df_within}", center=True),
                    *[
                        _
                        for mean, std in zip(group_means, group_stds)
                        for _ in (Cell(format_value_apa(mean), center=True), Cell(format_value_apa(std), center=True))
                    ],
                ]
            )
        )

    text = HTMLText(
        describe_single_test_multiple_variables(
            test_name="One-Way ANOVA",
            test_check="equality of means",
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property="have different means",
            no_property="have equal means",
            subgroup_results=subgroup_results,
        )
    )

    if not effect_size:
        return table, text

    post_hoc_items = []

    for col in significant_columns:
        significant = []
        posthoc_table = HTMLTable([])
        posthoc_table.table_caption = "Tukey's HSD post-hoc test results"
        posthoc_table.add_single_row_apa(
            Row([Cell()] + [Cell("p-value", col_span=len(group_names), center=True, border_bottom=True)])
        )
        posthoc_table.add_title_row_apa(Row([Cell()] + [Cell(name, center=True) for name in group_names]))
        posthoc_results = posthoc_tukey_hsd(df, val_col=col, group_col=grouping_column)

        for i, group_name in enumerate(group_names):
            row = [Cell(group_name, push_to_left=True)]
            for j in range(i + 1):
                if i == j:
                    row.append(Cell(MDASH, center=True))
                else:
                    row.append(Cell(format_p_apa(posthoc_results.iloc[i, j]), center=True))
                    if posthoc_results.iloc[i, j] < 0.05:
                        significant.append((i, j))
            posthoc_table.add_single_row_apa(Row(row))

        post_hoc_items.append(posthoc_table)

        post_hoc_items.append(
            HTMLText(
                f"The Tukey's HSD post-hoc test for {col} has revealed a "
                f"significant difference between the following groups: "
                + smart_comma_join(
                    [
                        f"{group_names[i]} and {group_names[j]} ({format_p_apa_full(posthoc_results.iloc[i, j])})"
                        for i, j in significant
                    ]
                )
                + "."
            )
        )

    return table, text, *post_hoc_items
