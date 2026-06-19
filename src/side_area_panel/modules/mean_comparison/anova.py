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
    format_p_apa_full,
    format_statistic_apa,
    format_value_apa,
    smart_comma_join,
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
def recalculate_mean_comparison_anova(
    data: Data,
    result: MeanComparisonResult,
    update,
) -> MeanComparisonResult:
    cfg = result.config
    selected_columns = cfg.column_selector[0]
    grouping_column = cfg.column_selector[1][0]
    # Apply filters and grouping-missing policy
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
                result.update_and_add_element(normality_table, "anova normality_table")
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
                result.update_and_add_element(normality_table, "anova normality_table")
    elif cfg.method == MeanComparisonMethod.AUTO.value:
        normal_columns, non_normal_columns, normality_table = process_normality_check(
            df=df,
            selected_columns=numeric_columns,
            grouping_column=grouping_column,
            verbal_indicators=cfg.verbal_indicators,
        )
        if (len(numeric_columns) > 0) and (cfg.assumption_checks != AssumptionChecksInGrouping.NEVER.value):
            result.update_and_add_element(normality_table, "anova normality_table")

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
                result.update_and_add_element(homogeneity_table, "anova homogeneity_table")
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
                result.update_and_add_element(homogeneity_table, "anova homogeneity_table")
    elif cfg.method == MeanComparisonMethod.AUTO.value:
        homogeneous_columns, non_homogeneous_columns, homogeneity_table = process_homogeneity_check(
            df=df,
            selected_columns=normal_columns
            if cfg.assumption_checks != AssumptionChecksInGrouping.NEVER.value
            else numeric_columns,
            grouping_column=grouping_column,
            verbal_indicators=cfg.verbal_indicators,
        )
        if (len(normal_columns) > 0) and (cfg.assumption_checks != AssumptionChecksInGrouping.NEVER.value):
            result.update_and_add_element(homogeneity_table, "anova homogeneity_table")

    if len(non_numeric_columns + non_normal_columns) > 0:
        items = process_non_normal_anova(
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
        )
        for i, item in enumerate(items):
            result.update_and_add_element(item, f"anova non_normal_{i}")

    if len(non_homogeneous_columns) > 0:
        items = process_non_homogeneous_anova(
            df=df,
            columns=non_homogeneous_columns,
            grouping_column=grouping_column,
            effect_size=cfg.effect_size,
            verbal_indicators=cfg.verbal_indicators,
        )
        for i, item in enumerate(items):
            result.update_and_add_element(item, f"anova non_homogeneous_{i}")

    if len(homogeneous_columns) > 0:
        items = process_homogeneous_anova(
            df=df,
            columns=homogeneous_columns,
            grouping_column=grouping_column,
            effect_size=cfg.effect_size,
            verbal_indicators=cfg.verbal_indicators,
        )
        for i, item in enumerate(items):
            result.update_and_add_element(item, f"anova homogeneous_{i}")

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
        result.update_and_add_element(plot_result, f"anova distribution_plot_{col}")

        box_plot_result = create_box_plot(
            groups=[df.loc[df[groupby_column] == groupby_value][col].dropna() for groupby_value in groupby_values],
            group_names=groupby_values,
            column=col,
            grouping_column=groupby_column,
        )
        result.update_and_add_element(box_plot_result, f"anova box_plot_{col}")
    return result


def process_non_normal_anova(
    df: pd.DataFrame, non_numeric_columns, non_normal_columns, grouping_column, effect_size, verbal_indicators=False
):
    show_sig = 1 if verbal_indicators else 0
    table = HTMLTableV2(table_caption=t("ttest.caption.kruskal"))

    group_names = df[grouping_column].unique().tolist()

    table.add_single_row_apa(
        Row([Cell()] * (4 + show_sig) + [Cell(name, center=True, col_span=2, border_bottom=True) for name in group_names])
    )

    table.add_title_row_apa(
        Row(
            [Cell(), Cell(t("ttest.col.kruskal_h"), center=True), Cell(t("common.p_value"), center=True)]
            + [Cell(t("verbal.col_significant"), center=True)] * show_sig
            + [Cell("df", center=True)]
            + [Cell(t("common.median"), center=True), Cell("IQR", center=True)] * len(group_names)
        )
    )

    columns = non_numeric_columns + non_normal_columns

    accepted_columns = []
    rejected_columns = []
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

        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(h_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                ]
                + [Cell(significance_verbal(p_val), center=True)] * show_sig
                + [Cell(str(len(groups) - 1), center=True)]
                + [
                    _
                    for median_value, iqr_value in zip(median, iqr)
                    for _ in (
                        Cell(format_value_apa(median_value), center=True),
                        Cell(format_value_apa(iqr_value), center=True),
                    )
                ]
            )
        )

    table.add_text(
        describe_single_test_multiple_variables(
            test_name=t("ttest.test.kruskal"),
            test_check=t("ttest.check.diff_groups"),
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property=t("ttest.prop.sig_diff"),
            no_property=t("ttest.prop.not_sig_diff"),
        )
    )

    if not effect_size:
        return (table,)

    post_hoc_items = []

    for col in significant_columns:
        significant = []
        post_hoc_table = HTMLTableV2(table_caption=t("ttest.caption.dunn"))
        post_hoc_table.add_single_row_apa(
            Row([Cell()] + [Cell(t("common.p_value"), col_span=len(group_names), center=True, border_bottom=True)])
        )
        post_hoc_table.add_title_row_apa(Row([Cell()] + [Cell(name, center=True) for name in group_names]))
        df_val = df[[col, grouping_column]].dropna(subset=[col])
        posthoc_results = posthoc_dunn(df_val, val_col=col, group_col=grouping_column)
        for i, group_name in enumerate(group_names):
            row = [Cell(group_name, push_to_left=True)]
            for j in range(i + 1):
                if i == j:
                    row.append(Cell(MDASH, center=True))
                else:
                    row.append(Cell(format_p_apa(posthoc_results.iloc[i, j]), center=True))
                    if posthoc_results.iloc[i, j] < 0.05:
                        significant.append((i, j))
            post_hoc_table.add_single_row_apa(Row(row))
        post_hoc_table.add_text(
            t(
                "ttest.posthoc_sentence",
                name=t("ttest.posthoc.dunn"),
                col=col,
                groups=smart_comma_join(
                    [
                        t(
                            "ttest.group_pair",
                            a=group_names[i],
                            b=group_names[j],
                            p=format_p_apa_full(posthoc_results.iloc[i, j]),
                        )
                        for i, j in significant
                    ]
                ),
            )
        )
        post_hoc_items.append(post_hoc_table)

    return table, *post_hoc_items


def process_non_homogeneous_anova(df: pd.DataFrame, columns, grouping_column, effect_size, verbal_indicators=False):
    show_sig = 1 if verbal_indicators else 0
    table = HTMLTableV2(table_caption=t("ttest.caption.welch_anova"))

    group_names = df[grouping_column].unique()

    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(), Cell(), Cell(), Cell()]
            + [Cell()] * show_sig
            + [Cell(name, center=True, col_span=2, border_bottom=True) for name in group_names]
        )
    )

    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell(t("ttest.col.welch_f"), center=True),
                Cell(t("common.p_value"), center=True),
            ]
            + [Cell(t("verbal.col_significant"), center=True)] * show_sig
            + [
                Cell("df1", center=True),
                Cell("df2", center=True),
                *[Cell(t("common.mean"), center=True), Cell("SD", center=True)] * len(group_names),
            ]
        )
    )

    accepted_columns = []
    rejected_columns = []
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

        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(f_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                    *([Cell(significance_verbal(p_val), center=True)] * show_sig),
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
            test_name=t("ttest.test.welch_anova"),
            test_check=t("ttest.check.equality_means"),
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property=t("ttest.prop.diff_means"),
            no_property=t("ttest.prop.equal_means"),
        )
    )

    if not effect_size:
        return (table,)

    post_hoc_items = []

    for col in significant_columns:
        significant = []
        post_hoc_table = HTMLTableV2(table_caption=t("ttest.caption.tamhane"))
        post_hoc_table.add_single_row_apa(
            Row([Cell()] + [Cell(t("common.p_value"), col_span=len(group_names), center=True, border_bottom=True)])
        )
        post_hoc_table.add_title_row_apa(Row([Cell()] + [Cell(name, center=True) for name in group_names]))
        df_val = df[[col, grouping_column]].dropna(subset=[col])
        posthoc_results = posthoc_tamhane(df_val, val_col=col, group_col=grouping_column)

        for i, group_name in enumerate(group_names):
            row = [Cell(group_name, push_to_left=True)]
            for j in range(i + 1):
                if i == j:
                    row.append(Cell(MDASH, center=True))
                else:
                    row.append(Cell(format_p_apa(posthoc_results.iloc[i, j]), center=True))
                    if posthoc_results.iloc[i, j] < 0.05:
                        significant.append((i, j))
            post_hoc_table.add_single_row_apa(Row(row))

        post_hoc_table.add_text(
            t(
                "ttest.posthoc_sentence",
                name=t("ttest.posthoc.tamhane"),
                col=col,
                groups=smart_comma_join(
                    [
                        t(
                            "ttest.group_pair",
                            a=group_names[i],
                            b=group_names[j],
                            p=format_p_apa_full(posthoc_results.iloc[i, j]),
                        )
                        for i, j in significant
                    ]
                ),
            )
        )
        post_hoc_items.append(post_hoc_table)

    return table, *post_hoc_items


def process_homogeneous_anova(df: pd.DataFrame, columns, grouping_column, effect_size, verbal_indicators=False):
    show_sig = 1 if verbal_indicators else 0
    table = HTMLTableV2(table_caption=t("ttest.caption.one_way_anova"))

    group_names = df[grouping_column].unique()

    # Adding header with group names and overall layout
    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(), Cell(), Cell(), Cell()]
            + [Cell()] * show_sig
            + [Cell(name, center=True, col_span=2, border_bottom=True) for name in group_names]
        )
    )

    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell(t("ttest.col.f_statistic"), center=True),
                Cell(t("common.p_value"), center=True),
            ]
            + [Cell(t("verbal.col_significant"), center=True)] * show_sig
            + [
                Cell("df1", center=True),
                Cell("df2", center=True),
                *[Cell(t("common.mean"), center=True), Cell("SD", center=True)] * len(group_names),
            ]
        )
    )
    accepted_columns = []
    rejected_columns = []
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

        # Adding the rows with calculated values
        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(f_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                    *([Cell(significance_verbal(p_val), center=True)] * show_sig),
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
            test_name=t("ttest.test.one_way_anova"),
            test_check=t("ttest.check.equality_means"),
            yes_columns=rejected_columns,
            no_columns=accepted_columns,
            yes_property=t("ttest.prop.diff_means"),
            no_property=t("ttest.prop.equal_means"),
        )
    )

    if not effect_size:
        return (table,)

    post_hoc_items = []

    for col in significant_columns:
        significant = []
        posthoc_table = HTMLTableV2(table_caption=t("ttest.caption.tukey"))
        posthoc_table.add_single_row_apa(
            Row([Cell()] + [Cell(t("common.p_value"), col_span=len(group_names), center=True, border_bottom=True)])
        )
        posthoc_table.add_title_row_apa(Row([Cell()] + [Cell(name, center=True) for name in group_names]))
        df_val = df[[col, grouping_column]].dropna(subset=[col])
        posthoc_results = posthoc_tukey_hsd(df_val, val_col=col, group_col=grouping_column)

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
            t(
                "ttest.posthoc_sentence",
                name=t("ttest.posthoc.tukey"),
                col=col,
                groups=smart_comma_join(
                    [
                        t(
                            "ttest.group_pair",
                            a=group_names[i],
                            b=group_names[j],
                            p=format_p_apa_full(posthoc_results.iloc[i, j]),
                        )
                        for i, j in significant
                    ]
                ),
            )
        )
        post_hoc_items.append(posthoc_table)

    return table, *post_hoc_items
