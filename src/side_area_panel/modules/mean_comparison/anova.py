#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import numpy as np
import pandas as pd
import pingouin as pg
from scikit_posthocs import posthoc_dunn, posthoc_tamhane, posthoc_tukey_hsd
from scipy import stats

from src.common.constant import MDASH, ColumnType
from src.common.decorators import log_function
from src.common.translations import t
from src.data.data import Data
from src.side_area_panel.modules.common.column_numbering import ColumnNumbering
from src.side_area_panel.modules.common.homogeneity import process_homogeneity_check
from src.side_area_panel.modules.common.normality import process_normality_check
from src.side_area_panel.modules.common.prose import ProseDetail, prose_enabled
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.utility import (
    format_p_apa,
    format_p_apa_full,
    format_r_apa,
    format_statistic_apa,
    format_value_apa,
    smart_comma_join,
)
from src.side_area_panel.modules.common.verbal.significance import significance_verbal
from src.side_area_panel.modules.common.verbal.test import TestResult, describe_grouped_test
from src.side_area_panel.modules.mean_comparison.constant import AssumptionChecksInGrouping, MeanComparisonMethod
from src.side_area_panel.modules.mean_comparison.group_plots import add_group_distribution_plots
from src.side_area_panel.modules.mean_comparison.mean_comparison_result import MeanComparisonResult
from src.side_area_panel.modules.mean_comparison.preprocessing import prepare_df_for_mean_comparison


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
                result.update_and_add_element(normality_table, "anova normality_table")
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
                result.update_and_add_element(normality_table, "anova normality_table")
    elif cfg.method == MeanComparisonMethod.AUTO.value:
        normal_columns, non_normal_columns, normality_table = process_normality_check(
            df=df,
            selected_columns=numeric_columns,
            grouping_column=grouping_column,
            verbal_indicators=cfg.verbal_indicators,
            numbering=numbering,
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
                numbering=numbering,
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
                numbering=numbering,
            )
            if len(normal_columns) > 0:
                result.update_and_add_element(homogeneity_table, "anova homogeneity_table")
    elif cfg.method == MeanComparisonMethod.AUTO.value:
        homogeneous_columns, non_homogeneous_columns, homogeneity_table = process_homogeneity_check(
            df=df,
            selected_columns=(
                normal_columns if cfg.assumption_checks != AssumptionChecksInGrouping.NEVER.value else numeric_columns
            ),
            grouping_column=grouping_column,
            verbal_indicators=cfg.verbal_indicators,
            numbering=numbering,
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
            numbering=numbering,
            prose_detail=cfg.interpretation,
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
            numbering=numbering,
            prose_detail=cfg.interpretation,
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
            numbering=numbering,
            prose_detail=cfg.interpretation,
        )
        for i, item in enumerate(items):
            result.update_and_add_element(item, f"anova homogeneous_{i}")

    if not cfg.plots:
        return result

    add_group_distribution_plots(result, df, selected_columns, numeric_columns, grouping_column, update, "anova")
    return result


def process_non_normal_anova(
    df: pd.DataFrame,
    non_numeric_columns,
    non_normal_columns,
    grouping_column,
    effect_size,
    verbal_indicators=False,
    numbering=None,
    prose_detail=ProseDetail.NONE.value,
):
    show_sig = 1 if verbal_indicators else 0
    numbering = numbering if numbering is not None else ColumnNumbering([], False)
    table = HTMLTableV2(table_caption=t("ttest.caption.kruskal"))

    group_names = df[grouping_column].unique().tolist()

    table.add_single_row_apa(
        Row(
            [Cell()] * (4 + show_sig)
            + [Cell(name, center=True, col_span=2, border_bottom=True) for name in group_names]
        )
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
                    Cell(numbering.label(col), push_to_left=True),
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

    # Prose report is optional; its detail level is set by the "Verbal report" dropdown.
    prose = describe_grouped_test(
        prose_detail,
        rejected_columns,
        accepted_columns,
        test_name=t("ttest.test.kruskal"),
        test_check=t("ttest.check.diff_groups"),
        yes_property=t("ttest.prop.sig_diff"),
        no_property=t("ttest.prop.not_sig_diff"),
    )
    if prose:
        table.add_text(prose)

    table.table_note = numbering.append_to_note(table.table_note or "")
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
        prose_enabled(prose_detail) and post_hoc_table.add_text(
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


def process_non_homogeneous_anova(
    df: pd.DataFrame,
    columns,
    grouping_column,
    effect_size,
    verbal_indicators=False,
    numbering=None,
    prose_detail=ProseDetail.NONE.value,
):
    show_sig = 1 if verbal_indicators else 0
    show_eff = 1 if effect_size else 0
    show_eff_verbal = 1 if (effect_size and verbal_indicators) else 0
    numbering = numbering if numbering is not None else ColumnNumbering([], False)
    table = HTMLTableV2(table_caption=t("ttest.caption.welch_anova"))

    group_names = df[grouping_column].unique()

    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(), Cell(), Cell(), Cell()]
            + [Cell()] * show_sig
            + [Cell(name, center=True, col_span=2, border_bottom=True) for name in group_names]
            + [Cell()] * show_eff
            + [Cell()] * show_eff_verbal
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
            + [Cell("&eta;&sup2;<sub>p</sub>", center=True)] * show_eff
            + [Cell(t("effect.col.magnitude"), center=True)] * show_eff_verbal
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
        # pingouin reports partial eta-squared (np2) for the Welch ANOVA.
        eta_sq = welch_result["np2"].values[0] if "np2" in welch_result.columns else np.nan

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
                    Cell(numbering.label(col), push_to_left=True),
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
                    *([Cell(format_r_apa(eta_sq), center=True)] * show_eff),
                    *([Cell(_eta_squared_magnitude(eta_sq), center=True)] * show_eff_verbal),
                ]
            )
        )

    # Prose report is optional; its detail level is set by the "Verbal report" dropdown.
    prose = describe_grouped_test(
        prose_detail,
        rejected_columns,
        accepted_columns,
        test_name=t("ttest.test.welch_anova"),
        test_check=t("ttest.check.equality_means"),
        yes_property=t("ttest.prop.diff_means"),
        no_property=t("ttest.prop.equal_means"),
    )
    if prose:
        table.add_text(prose)

    table.table_note = numbering.append_to_note(table.table_note or "")
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

        prose_enabled(prose_detail) and post_hoc_table.add_text(
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


def process_homogeneous_anova(
    df: pd.DataFrame,
    columns,
    grouping_column,
    effect_size,
    verbal_indicators=False,
    numbering=None,
    prose_detail=ProseDetail.NONE.value,
):
    show_sig = 1 if verbal_indicators else 0
    show_eff = 1 if effect_size else 0
    show_eff_verbal = 1 if (effect_size and verbal_indicators) else 0
    numbering = numbering if numbering is not None else ColumnNumbering([], False)
    table = HTMLTableV2(table_caption=t("ttest.caption.one_way_anova"))

    group_names = df[grouping_column].unique()

    # Adding header with group names and overall layout
    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(), Cell(), Cell(), Cell()]
            + [Cell()] * show_sig
            + [Cell(name, center=True, col_span=2, border_bottom=True) for name in group_names]
            + [Cell()] * show_eff
            + [Cell()] * show_eff_verbal
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
            + [Cell("&eta;&sup2;", center=True)] * show_eff
            + [Cell(t("effect.col.magnitude"), center=True)] * show_eff_verbal
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

        # Eta-squared from the F ratio: eta2 = (df_b * F) / (df_b * F + df_w).
        eta_sq = (
            (df_between * f_stat) / (df_between * f_stat + df_within)
            if np.isfinite(f_stat) and (df_between * f_stat + df_within) > 0
            else np.nan
        )

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
                    Cell(numbering.label(col), push_to_left=True),
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
                    *([Cell(format_r_apa(eta_sq), center=True)] * show_eff),
                    *([Cell(_eta_squared_magnitude(eta_sq), center=True)] * show_eff_verbal),
                ]
            )
        )

    # Prose report is optional; its detail level is set by the "Verbal report" dropdown.
    prose = describe_grouped_test(
        prose_detail,
        rejected_columns,
        accepted_columns,
        test_name=t("ttest.test.one_way_anova"),
        test_check=t("ttest.check.equality_means"),
        yes_property=t("ttest.prop.diff_means"),
        no_property=t("ttest.prop.equal_means"),
    )
    if prose:
        table.add_text(prose)

    table.table_note = numbering.append_to_note(table.table_note or "")
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
        prose_enabled(prose_detail) and posthoc_table.add_text(
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


def _eta_squared_magnitude(eta_sq) -> str:
    """Eta-squared bands: .01 small, .06 medium, .14 large (Cohen)."""
    if eta_sq is None or np.isnan(eta_sq):
        return "—"
    if eta_sq < 0.01:
        return t("effect.magnitude.negligible")
    if eta_sq < 0.06:
        return t("effect.magnitude.small")
    if eta_sq < 0.14:
        return t("effect.magnitude.medium")
    return t("effect.magnitude.large")
