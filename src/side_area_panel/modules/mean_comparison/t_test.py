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
from src.side_area_panel.modules.common.column_numbering import ColumnNumbering
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
    smart_comma_join,
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
from src.side_area_panel.modules.mean_comparison.group_plots import add_group_distribution_plots
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

    numbering = ColumnNumbering(list(selected_columns), enabled=bool(getattr(cfg, "number_columns", False)))

    normal_columns, non_normal_columns = [], []

    if cfg.method in [MeanComparisonMethod.HOMOGENEOUS.value, MeanComparisonMethod.INHOMOGENEOUS.value]:
        normal_columns, non_normal_columns = selected_columns, []
        if cfg.assumption_checks == AssumptionChecksInGrouping.ALWAYS.value:
            _, _, normality_table = process_normality_check(
                df=df,
                selected_columns=numeric_columns,
                grouping_column=grouping_column,
                verbal_indicators=cfg.verbal_indicators,
                numbering=numbering,
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
                numbering=numbering,
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
            numbering=numbering,
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
                numbering=numbering,
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
                numbering=numbering,
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
            numbering=numbering,
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
                numbering=numbering,
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
                confidence_intervals=cfg.confidence_intervals,
                numbering=numbering,
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
                confidence_intervals=cfg.confidence_intervals,
                numbering=numbering,
            ),
            "t_test homogeneous_table",
        )
    if not cfg.plots:
        return result

    add_group_distribution_plots(result, df, selected_columns, numeric_columns, grouping_column, update, "t_test")
    return result


def _cohen_d_ci(cohen_d: float, n1: int, n2: int) -> str:
    """Approximate 95% CI for Cohen's d via its large-sample standard error:
    SE = sqrt((n1+n2)/(n1*n2) + d^2 / (2*(n1+n2)))."""
    total = n1 + n2
    if n1 < 1 or n2 < 1 or total == 0:
        return "—"
    se = ((total) / (n1 * n2) + cohen_d**2 / (2 * total)) ** 0.5
    lo, hi = cohen_d - 1.96 * se, cohen_d + 1.96 * se
    return f"[{format_statistic_apa(lo)}, {format_statistic_apa(hi)}]"


def process_non_normal_t_test(
    df: pd.DataFrame, non_numeric_columns, non_normal_columns, grouping_column, effect_size, verbal_indicators=False, numbering=None
) -> HTMLTableV2:
    # The verbal magnitude column only makes sense alongside the numeric effect size; the
    # significance verbal follows the p-value whenever verbal indicators are on.
    show_verbal = 1 if (effect_size and verbal_indicators) else 0
    show_sig = 1 if verbal_indicators else 0
    numbering = numbering if numbering is not None else ColumnNumbering([], False)
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
                    Cell(numbering.label(col), push_to_left=True),
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

    # Prose report is optional (controlled by the "Verbal indicators" checkbox); the numeric
    # results stay in the table above regardless.
    verbal_indicators and table.add_text(
        describe_single_test_multiple_variables(
            test_name=t("ttest.test.mann_whitney"),
            test_check=t("ttest.check.diff_groups"),
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property=t("ttest.prop.sig_diff"),
            no_property=t("ttest.prop.not_sig_diff"),
        )
    )
    table.table_note = numbering.append_to_note(table.table_note or "")
    return table


def process_homogeneous_t_test(df: pd.DataFrame, columns, grouping_column, effect_size, verbal_indicators=False, confidence_intervals=False, numbering=None) -> HTMLTableV2:
    show_verbal = 1 if (effect_size and verbal_indicators) else 0
    show_sig = 1 if verbal_indicators else 0
    show_ci = 1 if (effect_size and confidence_intervals) else 0
    numbering = numbering if numbering is not None else ColumnNumbering([], False)
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
            + [Cell()] * show_ci
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
            + [Cell(t("common.ci_95"), center=True)] * show_ci
            + [Cell(t("effect.col.magnitude"), center=True)] * show_verbal
        )
    )

    accepted_columns = []
    rejected_columns = []
    ci_items = []

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
        ci_str = _cohen_d_ci(cohen_d, len(group1), len(group2))
        if show_ci:
            ci_items.append(f"{col} {ci_str}")
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
                    Cell(numbering.label(col), push_to_left=True),
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
                + [Cell(ci_str, center=True)] * show_ci
                + [Cell(cohen_d_magnitude(cohen_d), center=True)] * show_verbal
            )
        )

    # Prose report is optional (controlled by the "Verbal indicators" checkbox); the numeric
    # results stay in the table above regardless.
    verbal_indicators and table.add_text(
        describe_single_test_multiple_variables(
            test_name=t("ttest.test.ttest_independent"),
            test_check=t("ttest.check.equality_means"),
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property=t("ttest.prop.sig_diff"),
            no_property=t("ttest.prop.not_sig_diff"),
        )
    )
    if ci_items and verbal_indicators:
        table.add_text(t("ttest.ci_sentence", items=smart_comma_join(ci_items)))
    table.table_note = numbering.append_to_note(table.table_note or "")
    return table


def process_non_homogeneous_t_test(df: pd.DataFrame, columns, grouping_column, effect_size, verbal_indicators=False, confidence_intervals=False, numbering=None) -> HTMLTableV2:
    # inhomogeneous => Welch's t-test
    show_verbal = 1 if (effect_size and verbal_indicators) else 0
    show_sig = 1 if verbal_indicators else 0
    show_ci = 1 if (effect_size and confidence_intervals) else 0
    numbering = numbering if numbering is not None else ColumnNumbering([], False)
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
            + [Cell()] * show_ci
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
            + [Cell(t("common.ci_95"), center=True)] * show_ci
            + [Cell(t("effect.col.magnitude"), center=True)] * show_verbal
        )
    )

    accepted_columns = []
    rejected_columns = []
    ci_items = []

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
        ci_str = _cohen_d_ci(cohen_d, len(group1), len(group2))
        if show_ci:
            ci_items.append(f"{col} {ci_str}")

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
                    Cell(numbering.label(col), push_to_left=True),
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
                + [Cell(ci_str, center=True)] * show_ci
                + [Cell(cohen_d_magnitude(cohen_d), center=True)] * show_verbal
            )
        )

    # Prose report is optional (controlled by the "Verbal indicators" checkbox); the numeric
    # results stay in the table above regardless.
    verbal_indicators and table.add_text(
        describe_single_test_multiple_variables(
            test_name=t("ttest.test.welch_ttest"),
            test_check=t("ttest.check.equality_means"),
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property=t("ttest.prop.sig_diff"),
            no_property=t("ttest.prop.not_sig_diff"),
        )
    )
    if ci_items and verbal_indicators:
        table.add_text(t("ttest.ci_sentence", items=smart_comma_join(ci_items)))
    table.table_note = numbering.append_to_note(table.table_note or "")
    return table
