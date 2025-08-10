#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import gaussian_kde

from src._data_panel.data import Data
from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.common.qcolor import Colors
from src.modules.common.homogeneity import process_homogeneity_check
from src.modules.common.normality import process_normality_check
from src.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.modules.common.result.plot_result import Bar, BarPlotConfig, Line, LinePlotConfig, PlotV2
from src.modules.common.utility import format_p_apa, format_statistic_apa, format_value_apa
from src.modules.common.verbal.test import TestResult, describe_single_test_multiple_variables
from src.modules.descriptive.plot import create_box_plot
from src.modules.mean_comparison.constant import MeanComparisonMethod
from src.modules.mean_comparison.result import MeanComparisonResult


@log_function
def recalculate_mean_comparison_t_test(
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
        result.result_elements.append(
            process_non_normal_t_test(
                df=data.get_dataframe(
                    filters=result.config.filters,
                    columns=cfg.selected_columns + [cfg.grouping_column],
                    map_ordinal=True,
                ),
                non_numeric_columns=non_numeric_columns,
                non_normal_columns=non_normal_columns,
                grouping_column=cfg.grouping_column,
                means=cfg.means,
                effect_size=cfg.effect_size,
            )
        )

    if len(non_homogeneous_columns) > 0:
        result.result_elements.append(
            process_non_homogeneous_t_test(
                df=df,
                columns=non_homogeneous_columns,
                grouping_column=cfg.grouping_column,
                means=cfg.means,
                effect_size=cfg.effect_size,
            )
        )

    if len(homogeneous_columns) > 0:
        result.result_elements.append(
            process_homogeneous_t_test(
                df=df,
                columns=homogeneous_columns,
                grouping_column=cfg.grouping_column,
                means=cfg.means,
                effect_size=cfg.effect_size,
            )
        )
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


def process_non_normal_t_test(
    df: pd.DataFrame, non_numeric_columns, non_normal_columns, grouping_column, means, effect_size
) -> HTMLTableV2:
    table = HTMLTableV2(table_caption="Mann-Whitney U test")
    group1_name = df[grouping_column].unique()[0]
    group2_name = df[grouping_column].unique()[1]

    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(), Cell()]
            + [Cell(group1_name, center=True, col_span=2, border_bottom=True)] * means
            + [Cell(group2_name, center=True, col_span=2, border_bottom=True)] * means
            + [Cell()] * effect_size
        )
    )

    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell("Mann-Whitney U", center=True),
                Cell("p-value", center=True),
            ]
            + [
                Cell("Median", center=True),
                Cell("IQR", center=True),
            ]
            * means
            + [
                Cell("Median", center=True),
                Cell("IQR", center=True),
            ]
            * means
            + [
                Cell("r<sub>rb</sub>", center=True),
            ]
            * effect_size
        )
    )

    columns = non_numeric_columns + non_normal_columns

    accepted_columns = []
    rejected_columns = []
    subgroup_results = {}

    for col in columns:
        group1 = df[df[grouping_column] == df[grouping_column].unique()[0]][col]
        group2 = df[df[grouping_column] == df[grouping_column].unique()[1]][col]

        u1_stat, p_val = stats.mannwhitneyu(group1, group2)
        u2_stat = len(group1) * len(group2) - u1_stat
        u_stat = min(u1_stat, u2_stat)
        median, iqr = [group.median() for group in [group1, group2]], [
            group.quantile(0.75) - group.quantile(0.25) for group in [group1, group2]
        ]
        rank_biserial_correlation = 1 - 2 * u_stat / (len(group1) * len(group2))

        if effect_size:
            test_result = TestResult(
                variable=col, letter=["U", "r<sub>rb</sub>"], statistic=[u_stat, rank_biserial_correlation], p=p_val
            )
        else:
            test_result = TestResult(variable=col, letter="U", statistic=u_stat, p=p_val)

        if p_val > 0.05:
            accepted_columns.append(test_result)
        else:
            rejected_columns.append(test_result)

        subgroup_results[col] = [
            TestResult(variable=group1_name, letter=["Median", "IQR"], statistic=[median[0], iqr[0]], decimals=1),
            TestResult(variable=group2_name, letter=["Median", "IQR"], statistic=[median[1], iqr[1]], decimals=1),
        ]

        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(u_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                ]
                + [
                    Cell(format_value_apa(median[0]), center=True),
                    Cell(format_value_apa(iqr[0]), center=True),
                ]
                * means
                + [
                    Cell(format_value_apa(median[1]), center=True),
                    Cell(format_value_apa(iqr[1]), center=True),
                ]
                * means
                + [
                    Cell(format_statistic_apa(rank_biserial_correlation), center=True),
                ]
                * effect_size
            )
        )

    table.add_text(
        describe_single_test_multiple_variables(
            test_name="Mann-Whitney U test",
            test_check="difference between the groups",
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property="are significantly different across the groups",
            no_property="are not significantly different across the groups",
            subgroup_results=subgroup_results if means else None,
        )
    )
    return table


def process_homogeneous_t_test(df: pd.DataFrame, columns, grouping_column, means, effect_size) -> HTMLTableV2:
    table = HTMLTableV2(table_caption="Independent Samples T-test")

    group1_name = df[grouping_column].unique()[0]
    group2_name = df[grouping_column].unique()[1]

    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(), Cell(), Cell()]
            + [Cell(group1_name, center=True, col_span=2, border_bottom=True)] * means
            + [Cell(group2_name, center=True, col_span=2, border_bottom=True)] * means
            + [Cell()] * effect_size
        )
    )

    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell("t-statistic", center=True),
                Cell("p-value", center=True),
                Cell("df", center=True),
            ]
            + [
                Cell("Mean", center=True),
                Cell("SD", center=True),
                Cell("Mean", center=True),
                Cell("SD", center=True),
            ]
            * means
            + [Cell("Cohen's d", center=True)] * effect_size
        )
    )

    accepted_columns = []
    rejected_columns = []
    subgroup_results = {}

    for col in columns:
        group1 = df[df[grouping_column] == df[grouping_column].unique()[0]][col]
        group2 = df[df[grouping_column] == df[grouping_column].unique()[1]][col]
        t_test_result = stats.ttest_ind(group1, group2)
        t_stat, p_val, deg_free = t_test_result.statistic, t_test_result.pvalue, t_test_result.df
        mean, std = [group.mean() for group in [group1, group2]], [group.std() for group in [group1, group2]]
        cohen_s = (
            (std[0] ** 2 * (len(group1) - 1) + std[1] ** 2 * (len(group2) - 1)) / (len(group1) + len(group2) - 2)
        ) ** 0.5
        cohen_d = (mean[0] - mean[1]) / cohen_s
        if effect_size:
            test_result = TestResult(
                variable=col, letter=["t", "Cohen's d"], statistic=[t_stat, cohen_d], p=p_val, df=f"{deg_free:.1f}"
            )
        else:
            test_result = TestResult(variable=col, letter="t", statistic=t_stat, p=p_val, df=f"{deg_free:.0f}")

        if p_val > 0.05:
            accepted_columns.append(test_result)
        else:
            rejected_columns.append(test_result)
        subgroup_results[col] = [
            TestResult(variable=group1_name, letter=["M", "SD"], statistic=[mean[0], std[0]], decimals=1),
            TestResult(variable=group2_name, letter=["M", "SD"], statistic=[mean[1], std[1]], decimals=1),
        ]
        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(t_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                    Cell(f"{deg_free:.0f}", center=True),
                ]
                + [
                    Cell(format_value_apa(mean[0]), center=True),
                    Cell(format_value_apa(std[0]), center=True),
                    Cell(format_value_apa(mean[1]), center=True),
                    Cell(format_value_apa(std[1]), center=True),
                ]
                * means
                + [
                    Cell(format_statistic_apa(cohen_d), center=True),
                ]
                * effect_size
            )
        )

    table.add_text(
        describe_single_test_multiple_variables(
            test_name="Independent Samples T-test",
            test_check="equality of means",
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property="are significantly different across the groups",
            no_property="are not significantly different across the groups",
            subgroup_results=subgroup_results if means else None,
        )
    )
    return table


def process_non_homogeneous_t_test(df: pd.DataFrame, columns, grouping_column, means, effect_size) -> HTMLTableV2:
    # inhomogeneous => Welch's t-test
    table = HTMLTableV2(table_caption="Welch's T-test results")

    group1_name = df[grouping_column].unique()[0]
    group2_name = df[grouping_column].unique()[1]

    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(), Cell(), Cell()]
            + [Cell(group1_name, center=True, col_span=2, border_bottom=True)] * means
            + [Cell(group2_name, center=True, col_span=2, border_bottom=True)] * means
            + [Cell()] * effect_size
        )
    )

    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell("t-statistic", center=True),
                Cell("p-value", center=True),
                Cell("df", center=True),
            ]
            + [
                Cell("Mean", center=True),
                Cell("SD", center=True),
                Cell("Mean", center=True),
                Cell("SD", center=True),
            ]
            * means
            + [Cell("Cohen's d", center=True)] * effect_size
        )
    )

    accepted_columns = []
    rejected_columns = []
    subgroup_results = {}

    for col in columns:
        group1 = df[df[grouping_column] == df[grouping_column].unique()[0]][col]
        group2 = df[df[grouping_column] == df[grouping_column].unique()[1]][col]
        t_test_result = stats.ttest_ind(group1, group2, equal_var=False)
        t_stat, p_val, deg_free = t_test_result.statistic, t_test_result.pvalue, t_test_result.df
        mean, std = [group.mean() for group in [group1, group2]], [group.std() for group in [group1, group2]]
        cohen_s = (
            (std[0] ** 2 * (len(group1) - 1) + std[1] ** 2 * (len(group2) - 1)) / (len(group1) + len(group2) - 2)
        ) ** 0.5
        cohen_d = (mean[0] - mean[1]) / cohen_s

        if effect_size:
            test_result = TestResult(
                variable=col, letter=["t", "Cohen's d"], statistic=[t_stat, cohen_d], p=p_val, df=f"{deg_free:.1f}"
            )
        else:
            test_result = TestResult(variable=col, letter="t", statistic=t_stat, p=p_val, df=f"{deg_free:.0f}")

        if p_val > 0.05:
            accepted_columns.append(test_result)
        else:
            rejected_columns.append(test_result)
        subgroup_results[col] = [
            TestResult(variable=group1_name, letter=["M", "SD"], statistic=[mean[0], std[0]], decimals=1),
            TestResult(variable=group2_name, letter=["M", "SD"], statistic=[mean[1], std[1]], decimals=1),
        ]

        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(t_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                    Cell(f"{deg_free:.0f}", center=True),
                ]
                + [
                    Cell(format_value_apa(mean[0]), center=True),
                    Cell(format_value_apa(std[0]), center=True),
                    Cell(format_value_apa(mean[1]), center=True),
                    Cell(format_value_apa(std[1]), center=True),
                ]
                * means
                + [Cell(format_statistic_apa(cohen_d), center=True)] * effect_size
            )
        )

    table.add_text(
        describe_single_test_multiple_variables(
            test_name="Welch's T-test",
            test_check="equality of means",
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property="are significantly different across the groups",
            no_property="are not significantly different across the groups",
            subgroup_results=subgroup_results if means else None,
        )
    )
    return table
