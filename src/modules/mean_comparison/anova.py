#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import numpy as np
import pandas as pd
import pingouin as pg
from scikit_posthocs import posthoc_dunn, posthoc_tamhane, posthoc_tukey_hsd
from scipy import stats
from scipy.stats import gaussian_kde

from src.common.constant import MDASH, ColumnType
from src.common.decorators import log_function
from src.common.qcolor import Colors
from src.common.result.html_result import Cell, HTMLTableV2, Row
from src.common.result.plot_result import Bar, BarPlotConfig, Line, LinePlotConfig, PlotV2
from src.data_panel.data import Data
from src.modules.common.homogeneity import process_homogeneity_check
from src.modules.common.normality import process_normality_check
from src.modules.common.utility import (
    format_p_apa,
    format_p_apa_full,
    format_statistic_apa,
    format_value_apa,
    smart_comma_join,
)
from src.modules.common.verbal.test import TestResult, describe_single_test_multiple_variables
from src.modules.descriptive.plot import create_box_plot
from src.modules.mean_comparison.constant import MeanComparisonMethod
from src.modules.mean_comparison.result import MeanComparisonResult


@log_function
def recalculate_mean_comparison_anova(
    data: Data,
    result: MeanComparisonResult,
) -> MeanComparisonResult:
    cfg = result.config
    df = data.get_dataframe(filters=result.config.filters, columns=cfg.selected_columns + [cfg.grouping_column])

    numeric_columns = [col for col in cfg.selected_columns if data[col].column_type == ColumnType.NUMERIC]
    non_numeric_columns = [col for col in cfg.selected_columns if col not in numeric_columns]

    normal_columns, non_normal_columns = [], []
    if cfg.method in [MeanComparisonMethod.HOMOGENEOUS, MeanComparisonMethod.INHOMOGENEOUS]:
        normal_columns, non_normal_columns = cfg.selected_columns, []
    elif cfg.method == MeanComparisonMethod.NON_PARAMETRIC:
        normal_columns, non_normal_columns = [], cfg.selected_columns
    elif cfg.method == MeanComparisonMethod.AUTO:
        normal_columns, non_normal_columns, normality_table = process_normality_check(
            df=df,
            selected_columns=numeric_columns,
            grouping_column=cfg.grouping_column,
        )
        if len(numeric_columns) > 0:
            result.result_elements.append(normality_table)

    homogeneous_columns, non_homogeneous_columns = [], []
    if cfg.method == MeanComparisonMethod.HOMOGENEOUS:
        homogeneous_columns, non_homogeneous_columns = normal_columns, []
    elif cfg.method == MeanComparisonMethod.INHOMOGENEOUS:
        homogeneous_columns, non_homogeneous_columns = [], normal_columns
    elif cfg.method == MeanComparisonMethod.AUTO:
        homogeneous_columns, non_homogeneous_columns, homogeneity_table = process_homogeneity_check(
            df=df,
            selected_columns=normal_columns,
            grouping_column=cfg.grouping_column,
        )
        if len(normal_columns) > 0:
            result.result_elements.append(homogeneity_table)

    if len(non_numeric_columns + non_normal_columns) > 0:
        items = process_non_normal_anova(
            df=data.get_dataframe(
                filters=result.config.filters, columns=cfg.selected_columns + [cfg.grouping_column], map_ordinal=True
            ),
            non_numeric_columns=non_numeric_columns,
            non_normal_columns=non_normal_columns,
            grouping_column=cfg.grouping_column,
            means=cfg.means,
            effect_size=cfg.effect_size,
        )
        for item in items:
            result.result_elements.append(item)

    if len(non_homogeneous_columns) > 0:
        items = process_non_homogeneous_anova(
            df=df,
            columns=non_homogeneous_columns,
            grouping_column=cfg.grouping_column,
            means=cfg.means,
            effect_size=cfg.effect_size,
        )
        for item in items:
            result.result_elements.append(item)

    if len(homogeneous_columns) > 0:
        items = process_homogeneous_anova(
            df=df,
            columns=homogeneous_columns,
            grouping_column=cfg.grouping_column,
            means=cfg.means,
            effect_size=cfg.effect_size,
        )
        for item in items:
            result.result_elements.append(item)

    if not cfg.plots:
        return result

    groupby_column = cfg.grouping_column
    groupby_values = df[groupby_column].drop_duplicates().values
    numeric_columns = [col for col in cfg.selected_columns if data[col].column_type == ColumnType.NUMERIC]
    plot_result_elements = []
    for col in cfg.selected_columns:
        is_numeric = col in numeric_columns

        if not is_numeric:
            continue

        plots = []
        n_items = len(groupby_values)

        _, x_all = np.histogram(df[col], bins="auto", density=True)
        x_vals = np.linspace(df[col].min(), df[col].max(), 500)

        # | g 1 g 2 g |
        width = (x_all[1] - x_all[0]) * 0.9 / n_items
        gap = ((x_all[1] - x_all[0]) - width * len(groupby_values)) / (len(groupby_values) + 1)

        colors = Colors()

        for i, groupby_value in enumerate(groupby_values):
            df_subset = df.loc[df[groupby_column] == groupby_value]
            kde = gaussian_kde(df_subset[col].dropna())
            y_vals = kde(x_vals)
            color = colors.get_color_list()
            line_plot_config = LinePlotConfig(color=color)
            plot_line = Line(
                x=x_vals,
                y=y_vals,
                label=f"{groupby_value}",
                config=line_plot_config,
                legend_string=f"{groupby_value}",
            )
            plots.append(plot_line)

            y, x = np.histogram(df_subset[col], bins=x_all, density=True)
            bar_plot_config = BarPlotConfig(color=color)
            # bar plot # | g 1 g 2 g |
            plot_bar = Bar(
                x=x[:-1] + gap + width / 2 + i * (width + gap),
                y=y,
                width=width,
                label=f"{groupby_value}",
                config=bar_plot_config,
            )
            plots.append(plot_bar)

        plot_result = PlotV2(
            items=plots,
            title=f"Plot: Distribution of {col}",
            plot_title=f"Distribution of {col}",
            x_axis_title=col,
            y_axis_title="Density",
        )
        plot_result_elements.append(plot_result)

        box_plot_result = create_box_plot(
            groups=[df.loc[df[groupby_column] == groupby_value][col] for groupby_value in groupby_values],
            group_names=groupby_values,
            column=col,
            grouping_column=groupby_column,
        )

        plot_result_elements.append(box_plot_result)
    result.result_elements.extend(plot_result_elements)
    return result


def process_non_normal_anova(
    df: pd.DataFrame, non_numeric_columns, non_normal_columns, grouping_column, means, effect_size
):
    table = HTMLTableV2(table_caption="Kruskal-Wallis test")

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

    table.add_text(
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
        return (table,)

    post_hoc_items = []

    for col in significant_columns:
        significant = []
        posthoc_table = HTMLTableV2(table_caption="Dunn's post-hoc test results")
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
        posthoc_table.add_text(
            f"The Dunn's post-hoc test for {col} has revealed a "
            f"significant difference between the following groups: "
            + smart_comma_join(
                [
                    f"{group_names[i]} and {group_names[j]} ({format_p_apa_full(posthoc_results.iloc[i, j])})"
                    for i, j in significant
                ]
            )
            + "."
        )
        post_hoc_items.append(posthoc_table)

    return table, *post_hoc_items


def process_non_homogeneous_anova(df: pd.DataFrame, columns, grouping_column, means, effect_size):
    table = HTMLTableV2(table_caption="Welch's ANOVA results")

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

    table.add_text(
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
        return (table,)

    post_hoc_items = []

    for col in significant_columns:
        significant = []
        posthoc_table = HTMLTableV2(table_caption="Tamhane's T2 post-hoc test results")
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

        posthoc_table.add_text(
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
        post_hoc_items.append(posthoc_table)

    return table, *post_hoc_items


def process_homogeneous_anova(df: pd.DataFrame, columns, grouping_column, means, effect_size):
    table = HTMLTableV2(table_caption="One-Way ANOVA results")

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

    table.add_text(
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
        return (table,)

    post_hoc_items = []

    for col in significant_columns:
        significant = []
        posthoc_table = HTMLTableV2(table_caption="Tukey's HSD post-hoc test results")
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
        posthoc_table.add_text(
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
        post_hoc_items.append(posthoc_table)

    return table, *post_hoc_items
