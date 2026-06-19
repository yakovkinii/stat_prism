#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import gaussian_kde

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.common.qcolor import Colors
from src.common.translations import t
from src.data.data import Data
from src.side_area_panel.modules.common.homogeneity import process_homogeneity_check
from src.side_area_panel.modules.common.normality import process_normality_check
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.result.plot_result import (
    Bar,
    BarPlotConfig,
    Line,
    LinePlotConfig,
    PlotV2,
)
from src.side_area_panel.modules.common.utility import (
    format_p_apa,
    format_statistic_apa,
    format_value_apa,
)
from src.side_area_panel.modules.common.verbal.effect_size import (
    cohen_d_magnitude,
    correlation_magnitude,
)
from src.side_area_panel.modules.common.verbal.significance import significance_verbal
from src.side_area_panel.modules.common.verbal.test import (
    TestResult,
    describe_single_test_multiple_variables,
)
from src.side_area_panel.modules.descriptive.plot import create_box_plot
from src.side_area_panel.modules.mean_comparison.constant import (
    AssumptionChecksInGrouping,
    MeanComparisonMethod,
)
from src.side_area_panel.modules.mean_comparison.mean_comparison_result import (
    MeanComparisonResult,
)
from src.side_area_panel.modules.mean_comparison.preprocessing import (
    prepare_df_for_mean_comparison,
)


@log_function
def recalculate_mean_comparison_t_test(
    data: Data,
    result: MeanComparisonResult,
    update,
) -> MeanComparisonResult:
    cfg = result.config
    selected_columns = cfg.column_selector[0]

    grouping_column = cfg.column_selector[1][0]
    df = prepare_df_for_mean_comparison(data=data, cfg=cfg)

    numeric_columns = [col for col in selected_columns if data[col].column_type == ColumnType.NUMERIC]
    non_numeric_columns = [col for col in selected_columns if col not in numeric_columns]

    normal_columns, non_normal_columns = [], []

    if cfg.method in [MeanComparisonMethod.HOMOGENEOUS.value, MeanComparisonMethod.INHOMOGENEOUS.value]:
        normal_columns, non_normal_columns = selected_columns, []
        if cfg.assumption_checks == AssumptionChecksInGrouping.ALWAYS.value:
            _, _, normality_table = process_normality_check(
                df=df,
                selected_columns=numeric_columns,
                grouping_column=grouping_column,
                verbal_indicators=cfg.verbal_indicators,
            )
            if len(numeric_columns) > 0:
                result.update_and_add_element(
                    normality_table,
                    "t_test normality_table",
                )

    elif cfg.method == MeanComparisonMethod.NON_PARAMETRIC.value:
        normal_columns, non_normal_columns = [], selected_columns
        if cfg.assumption_checks == AssumptionChecksInGrouping.ALWAYS.value:
            _, _, normality_table = process_normality_check(
                df=df,
                selected_columns=numeric_columns,
                grouping_column=grouping_column,
                verbal_indicators=cfg.verbal_indicators,
            )
            if len(numeric_columns) > 0:
                result.update_and_add_element(
                    normality_table,
                    "t_test normality_table",
                )
    elif cfg.method == MeanComparisonMethod.AUTO.value:
        normal_columns, non_normal_columns, normality_table = process_normality_check(
            df=df,
            selected_columns=numeric_columns,
            grouping_column=grouping_column,
            verbal_indicators=cfg.verbal_indicators,
        )
        if (len(numeric_columns) > 0) and not (cfg.assumption_checks == AssumptionChecksInGrouping.NEVER.value):
            result.update_and_add_element(
                normality_table,
                "t_test normality_table",
            )

    homogeneous_columns, non_homogeneous_columns = [], []
    if cfg.method == MeanComparisonMethod.HOMOGENEOUS.value:
        homogeneous_columns, non_homogeneous_columns = normal_columns, []
        if cfg.assumption_checks == AssumptionChecksInGrouping.ALWAYS.value:
            _, _, homogeneity_table = process_homogeneity_check(
                df=df,
                selected_columns=numeric_columns,
                grouping_column=grouping_column,
                verbal_indicators=cfg.verbal_indicators,
            )
            if len(normal_columns) > 0:
                result.update_and_add_element(
                    homogeneity_table,
                    "t_test homogeneity_table",
                )
    elif cfg.method == MeanComparisonMethod.INHOMOGENEOUS.value:
        homogeneous_columns, non_homogeneous_columns = [], normal_columns
        if cfg.assumption_checks == AssumptionChecksInGrouping.ALWAYS.value:
            _, _, homogeneity_table = process_homogeneity_check(
                df=df,
                selected_columns=numeric_columns,
                grouping_column=grouping_column,
                verbal_indicators=cfg.verbal_indicators,
            )
            if len(normal_columns) > 0:
                result.update_and_add_element(
                    homogeneity_table,
                    "t_test homogeneity_table",
                )
    elif cfg.method == MeanComparisonMethod.AUTO.value:
        homogeneous_columns, non_homogeneous_columns, homogeneity_table = process_homogeneity_check(
            df=df,
            selected_columns=normal_columns
            if (cfg.assumption_checks != AssumptionChecksInGrouping.ALWAYS.value)
            else numeric_columns,
            grouping_column=grouping_column,
            verbal_indicators=cfg.verbal_indicators,
        )
        if (len(normal_columns) > 0) and not (cfg.assumption_checks == AssumptionChecksInGrouping.NEVER.value):
            result.update_and_add_element(
                homogeneity_table,
                "t_test homogeneity_table",
            )
    if len(non_numeric_columns + non_normal_columns) > 0:
        result.update_and_add_element(
            process_non_normal_t_test(
                df=prepare_df_for_mean_comparison(
                    data=data,
                    cfg=cfg,
                    map_ordinal=True,
                ),
                non_numeric_columns=non_numeric_columns,
                non_normal_columns=non_normal_columns,
                grouping_column=grouping_column,
                effect_size=cfg.effect_size,
                verbal_indicators=cfg.verbal_indicators,
            ),
            "t_test non_normal_table",
        )

    if len(non_homogeneous_columns) > 0:
        result.update_and_add_element(
            process_non_homogeneous_t_test(
                df=df,
                columns=non_homogeneous_columns,
                grouping_column=grouping_column,
                effect_size=cfg.effect_size,
                verbal_indicators=cfg.verbal_indicators,
            ),
            "t_test non_homogeneous_table",
        )

    if len(homogeneous_columns) > 0:
        result.update_and_add_element(
            process_homogeneous_t_test(
                df=df,
                columns=homogeneous_columns,
                grouping_column=grouping_column,
                effect_size=cfg.effect_size,
                verbal_indicators=cfg.verbal_indicators,
            ),
            "t_test homogeneous_table",
        )
    if not cfg.plots:
        return result

    groupby_column = grouping_column
    groupby_values = df[groupby_column].drop_duplicates().values
    for idx, col in enumerate(selected_columns):
        update(10 + 80 * (idx + 1) / len(selected_columns))
        is_numeric = col in numeric_columns
        if not is_numeric:
            continue

        plots = []
        n_items = len(groupby_values)

        # Drop NaNs in the value column explicitly before histogram/KDE
        col_series = df[col].dropna()
        if col_series.empty:
            continue
        _, x_all = np.histogram(col_series, bins="auto", density=True)
        x_vals = np.linspace(col_series.min(), col_series.max(), 500)

        # | g 1 g 2 g |
        width = (x_all[1] - x_all[0]) * 0.9 / n_items if len(x_all) > 1 else 0.9 / max(n_items, 1)
        gap = ((x_all[1] - x_all[0]) - width * len(groupby_values)) / (len(groupby_values) + 1) if len(x_all) > 1 else 0

        colors = Colors()

        for i, groupby_value in enumerate(groupby_values):
            df_subset = df.loc[df[groupby_column] == groupby_value]
            series = df_subset[col].dropna()
            if series.empty:
                continue
            kde = gaussian_kde(series)
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

            y, x = np.histogram(series, bins=x_all, density=True)
            bar_plot_config = BarPlotConfig(color=color)
            # bar plot # | g 1 g 2 g |
            plot_bar = Bar(
                x=x[:-1] + gap + width / 2 + i * (width + gap) if len(x) > 1 else x,
                y=y,
                width=width,
                label=f"{groupby_value}",
                config=bar_plot_config,
            )
            plots.append(plot_bar)

        plot_result = PlotV2(
            items=plots,
            title=t("ttest.plot.distribution_tab", col=col),
            plot_title=t("ttest.plot.distribution", col=col),
            x_axis_title=col,
            y_axis_title=t("ttest.plot.density"),
        )
        result.update_and_add_element(
            plot_result,
            f"t_test distribution_plot_{col}",
        )

        box_plot_result = create_box_plot(
            groups=[df.loc[df[groupby_column] == groupby_value][col].dropna() for groupby_value in groupby_values],
            group_names=groupby_values,
            column=col,
            grouping_column=groupby_column,
        )
        result.update_and_add_element(
            box_plot_result,
            f"t_test box_plot_{col}",
        )
    return result


def process_non_normal_t_test(
    df: pd.DataFrame, non_numeric_columns, non_normal_columns, grouping_column, effect_size, verbal_indicators=False
) -> HTMLTableV2:
    # The verbal magnitude column only makes sense alongside the numeric effect size; the
    # significance verbal follows the p-value whenever verbal indicators are on.
    show_verbal = 1 if (effect_size and verbal_indicators) else 0
    show_sig = 1 if verbal_indicators else 0
    table = HTMLTableV2(table_caption=t("ttest.caption.mann_whitney"))
    group1_name = df[grouping_column].unique()[0]
    group2_name = df[grouping_column].unique()[1]

    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(), Cell()]
            + [Cell()] * show_sig
            + [Cell(group1_name, center=True, col_span=2, border_bottom=True)]
            + [Cell(group2_name, center=True, col_span=2, border_bottom=True)]
            + [Cell()] * effect_size
            + [Cell()] * show_verbal
        )
    )

    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell(t("ttest.col.mann_whitney_u"), center=True),
                Cell(t("common.p_value"), center=True),
            ]
            + [Cell(t("verbal.col_significant"), center=True)] * show_sig
            + [
                Cell(t("common.median"), center=True),
                Cell("IQR", center=True),
            ]
            + [
                Cell(t("common.median"), center=True),
                Cell("IQR", center=True),
            ]
            + [
                Cell("r<sub>rb</sub>", center=True),
            ]
            * effect_size
            + [Cell(t("effect.col.magnitude"), center=True)] * show_verbal
        )
    )

    columns = non_numeric_columns + non_normal_columns

    accepted_columns = []
    rejected_columns = []

    for col in columns:
        group1 = df[df[grouping_column] == df[grouping_column].unique()[0]][col].dropna()
        group2 = df[df[grouping_column] == df[grouping_column].unique()[1]][col].dropna()

        if group1.empty or group2.empty:
            continue

        u1_stat, p_val = stats.mannwhitneyu(group1, group2)
        u2_stat = len(group1) * len(group2) - u1_stat
        u_stat = min(u1_stat, u2_stat)
        median, iqr = [group.median() for group in [group1, group2]], [
            group.quantile(0.75) - group.quantile(0.25) for group in [group1, group2]
        ]
        # Directional rank-biserial correlation (keeps the sign of the effect):
        # computed from U1 so a positive value means group 1 tends to rank higher.
        rank_biserial_correlation = 1 - 2 * u1_stat / (len(group1) * len(group2))

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

        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(u_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                ]
                + [Cell(significance_verbal(p_val), center=True)] * show_sig
                + [
                    Cell(format_value_apa(median[0]), center=True),
                    Cell(format_value_apa(iqr[0]), center=True),
                ]
                + [
                    Cell(format_value_apa(median[1]), center=True),
                    Cell(format_value_apa(iqr[1]), center=True),
                ]
                + [
                    Cell(format_statistic_apa(rank_biserial_correlation), center=True),
                ]
                * effect_size
                + [Cell(correlation_magnitude(rank_biserial_correlation), center=True)] * show_verbal
            )
        )

    table.add_text(
        describe_single_test_multiple_variables(
            test_name=t("ttest.test.mann_whitney"),
            test_check=t("ttest.check.diff_groups"),
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property=t("ttest.prop.sig_diff"),
            no_property=t("ttest.prop.not_sig_diff"),
        )
    )
    return table


def process_homogeneous_t_test(df: pd.DataFrame, columns, grouping_column, effect_size, verbal_indicators=False) -> HTMLTableV2:
    show_verbal = 1 if (effect_size and verbal_indicators) else 0
    show_sig = 1 if verbal_indicators else 0
    table = HTMLTableV2(table_caption=t("ttest.caption.ttest_independent"))

    group1_name = df[grouping_column].unique()[0]
    group2_name = df[grouping_column].unique()[1]

    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(), Cell(), Cell()]
            + [Cell()] * show_sig
            + [Cell(group1_name, center=True, col_span=2, border_bottom=True)]
            + [Cell(group2_name, center=True, col_span=2, border_bottom=True)]
            + [Cell()] * effect_size
            + [Cell()] * show_verbal
        )
    )

    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell(t("ttest.col.t_statistic"), center=True),
                Cell(t("common.p_value"), center=True),
            ]
            + [Cell(t("verbal.col_significant"), center=True)] * show_sig
            + [Cell("df", center=True)]
            + [
                Cell(t("common.mean"), center=True),
                Cell("SD", center=True),
                Cell(t("common.mean"), center=True),
                Cell("SD", center=True),
            ]
            + [Cell("Cohen's d", center=True)] * effect_size
            + [Cell(t("effect.col.magnitude"), center=True)] * show_verbal
        )
    )

    accepted_columns = []
    rejected_columns = []

    for col in columns:
        group1 = df[df[grouping_column] == df[grouping_column].unique()[0]][col].dropna()
        group2 = df[df[grouping_column] == df[grouping_column].unique()[1]][col].dropna()
        if group1.empty or group2.empty:
            continue
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
        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(t_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                ]
                + [Cell(significance_verbal(p_val), center=True)] * show_sig
                + [
                    Cell(f"{deg_free:.0f}", center=True),
                ]
                + [
                    Cell(format_value_apa(mean[0]), center=True),
                    Cell(format_value_apa(std[0]), center=True),
                    Cell(format_value_apa(mean[1]), center=True),
                    Cell(format_value_apa(std[1]), center=True),
                ]
                + [
                    Cell(format_statistic_apa(cohen_d), center=True),
                ]
                * effect_size
                + [Cell(cohen_d_magnitude(cohen_d), center=True)] * show_verbal
            )
        )

    table.add_text(
        describe_single_test_multiple_variables(
            test_name=t("ttest.test.ttest_independent"),
            test_check=t("ttest.check.equality_means"),
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property=t("ttest.prop.sig_diff"),
            no_property=t("ttest.prop.not_sig_diff"),
        )
    )
    return table


def process_non_homogeneous_t_test(df: pd.DataFrame, columns, grouping_column, effect_size, verbal_indicators=False) -> HTMLTableV2:
    # inhomogeneous => Welch's t-test
    show_verbal = 1 if (effect_size and verbal_indicators) else 0
    show_sig = 1 if verbal_indicators else 0
    table = HTMLTableV2(table_caption=t("ttest.caption.welch_ttest"))

    group1_name = df[grouping_column].unique()[0]
    group2_name = df[grouping_column].unique()[1]

    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(), Cell(), Cell()]
            + [Cell()] * show_sig
            + [Cell(group1_name, center=True, col_span=2, border_bottom=True)]
            + [Cell(group2_name, center=True, col_span=2, border_bottom=True)]
            + [Cell()] * effect_size
            + [Cell()] * show_verbal
        )
    )

    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell(t("ttest.col.t_statistic"), center=True),
                Cell(t("common.p_value"), center=True),
            ]
            + [Cell(t("verbal.col_significant"), center=True)] * show_sig
            + [Cell("df", center=True)]
            + [
                Cell(t("common.mean"), center=True),
                Cell("SD", center=True),
                Cell(t("common.mean"), center=True),
                Cell("SD", center=True),
            ]
            + [Cell("Cohen's d", center=True)] * effect_size
            + [Cell(t("effect.col.magnitude"), center=True)] * show_verbal
        )
    )

    accepted_columns = []
    rejected_columns = []

    for col in columns:
        group1 = df[df[grouping_column] == df[grouping_column].unique()[0]][col].dropna()
        group2 = df[df[grouping_column] == df[grouping_column].unique()[1]][col].dropna()
        if group1.empty or group2.empty:
            continue
        t_test_result = stats.ttest_ind(group1, group2, equal_var=False)
        t_stat, p_val, deg_free = t_test_result.statistic, t_test_result.pvalue, t_test_result.df
        mean, std = [group.mean() for group in [group1, group2]], [group.std() for group in [group1, group2]]
        # Welch (unequal variances): standardize by the root-mean of the two
        # group variances rather than the pooled SD, which assumes equal variance.
        cohen_s = ((std[0] ** 2 + std[1] ** 2) / 2) ** 0.5
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

        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(t_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                ]
                + [Cell(significance_verbal(p_val), center=True)] * show_sig
                + [
                    Cell(f"{deg_free:.0f}", center=True),
                ]
                + [
                    Cell(format_value_apa(mean[0]), center=True),
                    Cell(format_value_apa(std[0]), center=True),
                    Cell(format_value_apa(mean[1]), center=True),
                    Cell(format_value_apa(std[1]), center=True),
                ]
                + [Cell(format_statistic_apa(cohen_d), center=True)] * effect_size
                + [Cell(cohen_d_magnitude(cohen_d), center=True)] * show_verbal
            )
        )

    table.add_text(
        describe_single_test_multiple_variables(
            test_name=t("ttest.test.welch_ttest"),
            test_check=t("ttest.check.equality_means"),
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property=t("ttest.prop.sig_diff"),
            no_property=t("ttest.prop.not_sig_diff"),
        )
    )
    return table
