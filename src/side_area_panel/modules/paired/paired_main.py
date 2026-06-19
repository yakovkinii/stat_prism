#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

import pandas as pd
import pingouin as pg
from scikit_posthocs import posthoc_nemenyi_friedman
from scipy import stats

from src.common.constant import MDASH
from src.common.decorators import log_function
from src.common.translations import t
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.utility import (
    format_p_apa,
    format_p_apa_full,
    format_statistic_apa,
    format_value_apa,
    smart_comma_join,
)
from src.side_area_panel.modules.common.verbal.effect_size import (
    cohen_d_magnitude,
    correlation_magnitude,
)
from src.side_area_panel.modules.common.verbal.significance import (
    assumption_met_verbal,
    significance_verbal,
)
from src.side_area_panel.modules.common.verbal.test import TestResult
from src.side_area_panel.modules.descriptive.plot import create_box_plot
from src.side_area_panel.modules.paired.constant import (
    PairedAssumptionChecks,
    PairedMethod,
)
from src.side_area_panel.modules.paired.paired_result import PairedResult
from src.side_area_panel.modules.paired.paired_ui import Elements

# Smallest number of complete cases the tests can run on.
_MIN_CASES = 3
# Subject / condition / value column names used internally for the long-format frame.
_SUBJECT = "__subject__"
_CONDITION = "__condition__"
_VALUE = "__value__"


def _fail(result: PairedResult, message: str) -> PairedResult:
    """Show a validation message to the user and log it, then stop."""
    logging.warning("Paired/Repeated Measures: %s", message)
    result.set_error(message)
    return result


@log_function
def recalculate_paired_study(elements: Elements, result: PairedResult, update) -> PairedResult:
    """Validate the inputs, then route to the paired family (two conditions) or the
    repeated-measures family (three or more conditions), parametric or non-parametric.
    Unexpected exceptions are handled centrally by the panel's recalculate()."""
    cfg = result.config
    result.result_elements = []

    conditions = cfg.column_selector[0]
    if len(conditions) < 2:
        return _fail(result, t("paired.error.min_conditions"))

    if cfg.method == PairedMethod.AUTO.value and cfg.assumption_checks == PairedAssumptionChecks.NEVER.value:
        return _fail(result, t("paired.error.auto_no_assumptions"))

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    # Repeated measures need complete cases: drop a respondent missing any condition.
    wide = data.get_dataframe(columns=conditions, map_ordinal=True).dropna().reset_index(drop=True)
    if len(wide) < _MIN_CASES:
        return _fail(result, t("paired.error.insufficient", n=len(wide)))

    result.title_context = ", ".join(col[:16] for col in conditions)
    update(10)

    two_conditions = len(conditions) == 2
    parametric = _resolve_parametric(cfg, wide, conditions, two_conditions)

    result.update_and_add_element(_descriptives_table(wide, conditions), "paired descriptives")

    if cfg.assumption_checks != PairedAssumptionChecks.NEVER.value:
        result.update_and_add_element(
            _normality_table(wide, conditions, two_conditions, cfg.verbal_indicators),
            "paired normality",
        )
    update(40)

    if two_conditions:
        if parametric:
            _paired_t_test(result, wide, conditions, cfg)
        else:
            _wilcoxon_test(result, wide, conditions, cfg)
    else:
        if parametric:
            _rm_anova(result, wide, conditions, cfg)
        else:
            _friedman(result, wide, conditions, cfg)
    update(70)

    if cfg.plots:
        _add_plots(result, wide, conditions)

    update(100)
    return result


def _resolve_parametric(cfg, wide, conditions, two_conditions) -> bool:
    """Whether to use the parametric family. AUTO decides from the Shapiro-Wilk check:
    on the paired differences (two conditions) or per condition (three or more)."""
    if cfg.method == PairedMethod.PARAMETRIC.value:
        return True
    if cfg.method == PairedMethod.NON_PARAMETRIC.value:
        return False
    # AUTO
    if two_conditions:
        diff = wide[conditions[0]] - wide[conditions[1]]
        return stats.shapiro(diff).pvalue > 0.05
    return all(stats.shapiro(wide[col]).pvalue > 0.05 for col in conditions)


def _to_long(wide: pd.DataFrame, conditions) -> pd.DataFrame:
    """Tidy long format (subject, condition, value) for the pingouin within-subject tests."""
    frame = wide[conditions].copy()
    frame[_SUBJECT] = frame.index
    return frame.melt(
        id_vars=_SUBJECT, value_vars=list(conditions), var_name=_CONDITION, value_name=_VALUE
    )


def _descriptives_table(wide: pd.DataFrame, conditions) -> HTMLTableV2:
    table = HTMLTableV2(table_caption=t("paired.caption.descriptives"))
    table.add_title_row_apa(
        Row(
            [
                Cell(t("paired.col.condition")),
                Cell(t("paired.col.n"), center=True),
                Cell(t("common.mean"), center=True),
                Cell("SD", center=True),
                Cell(t("common.median"), center=True),
                Cell("IQR", center=True),
            ]
        )
    )
    for col in conditions:
        series = wide[col]
        iqr = series.quantile(0.75) - series.quantile(0.25)
        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(str(len(series)), center=True),
                    Cell(format_value_apa(series.mean()), center=True),
                    Cell(format_value_apa(series.std()), center=True),
                    Cell(format_value_apa(series.median()), center=True),
                    Cell(format_value_apa(iqr), center=True),
                ]
            )
        )
    return table


def _normality_table(wide: pd.DataFrame, conditions, two_conditions, verbal_indicators) -> HTMLTableV2:
    show_verbal = 1 if verbal_indicators else 0
    table = HTMLTableV2(table_caption=t("paired.caption.normality"))
    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell("W", center=True),
                Cell(t("common.p_value"), center=True),
            ]
            + [Cell(t("paired.col.normal"), center=True)] * show_verbal
        )
    )

    if two_conditions:
        diff = wide[conditions[0]] - wide[conditions[1]]
        w_stat, p_val = stats.shapiro(diff)
        table.add_single_row_apa(
            Row(
                [
                    Cell(t("paired.row.differences"), push_to_left=True),
                    Cell(format_statistic_apa(w_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                ]
                + [Cell(assumption_met_verbal(p_val), center=True)] * show_verbal
            )
        )
        return table

    for col in conditions:
        w_stat, p_val = stats.shapiro(wide[col])
        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(w_stat), center=True),
                    Cell(format_p_apa(p_val), center=True),
                ]
                + [Cell(assumption_met_verbal(p_val), center=True)] * show_verbal
            )
        )

    # Sphericity (Mauchly) -- relevant only with 3+ conditions.
    spher = pg.sphericity(data=_to_long(wide, conditions), dv=_VALUE, within=_CONDITION, subject=_SUBJECT)
    table.add_single_row_apa(
        Row(
            [
                Cell(t("paired.row.sphericity"), push_to_left=True),
                Cell(format_statistic_apa(spher.W), center=True),
                Cell(format_p_apa(spher.pval), center=True),
            ]
            + [Cell(assumption_met_verbal(spher.pval), center=True)] * show_verbal
        )
    )
    return table


def _result_table(caption, headers, values, test_result: TestResult, test_name, p_val) -> HTMLTableV2:
    """A single-row omnibus table: a header row, one statistics row, and a verbal summary."""
    table = HTMLTableV2(table_caption=caption)
    table.add_title_row_apa(Row([Cell(label, center=True) for label in headers]))
    table.add_single_row_apa(Row([Cell(value, center=True) for value in values]))
    table.add_text(
        t(
            "paired.verbal.result",
            test=test_name,
            conclusion=significance_verbal(p_val),
            stats=str(test_result),
        )
    )
    return table


def _paired_t_test(result, wide, conditions, cfg):
    show_verbal = 1 if (cfg.effect_size and cfg.verbal_indicators) else 0
    a, b = conditions[0], conditions[1]
    diff = wide[a] - wide[b]
    t_res = stats.ttest_rel(wide[a], wide[b])
    t_stat, p_val, df = t_res.statistic, t_res.pvalue, len(wide) - 1
    cohen_dz = diff.mean() / diff.std()

    headers = ["t", "df", t("common.p_value")]
    values = [format_statistic_apa(t_stat), str(df), format_p_apa(p_val)]
    headers += [t("verbal.col_significant")] * (1 if cfg.verbal_indicators else 0)
    values += [significance_verbal(p_val)] * (1 if cfg.verbal_indicators else 0)
    headers += ["d<sub>z</sub>"] * (1 if cfg.effect_size else 0)
    values += [format_statistic_apa(cohen_dz)] * (1 if cfg.effect_size else 0)
    headers += [t("effect.col.magnitude")] * show_verbal
    values += [cohen_d_magnitude(cohen_dz)] * show_verbal

    if cfg.effect_size:
        test_result = TestResult(variable="", letter=["t", "d<sub>z</sub>"], statistic=[t_stat, cohen_dz], p=p_val, df=df)
    else:
        test_result = TestResult(variable="", letter="t", statistic=t_stat, p=p_val, df=df)

    result.update_and_add_element(
        _result_table(t("paired.caption.paired_t"), headers, values, test_result, t("paired.test.paired_t"), p_val),
        "paired omnibus",
    )


def _wilcoxon_test(result, wide, conditions, cfg):
    show_verbal = 1 if (cfg.effect_size and cfg.verbal_indicators) else 0
    a, b = conditions[0], conditions[1]
    res = pg.wilcoxon(wide[a], wide[b])
    w_stat = res["W-val"].values[0]
    p_val = res["p-val"].values[0]
    rbc = res["RBC"].values[0]

    headers = ["W", t("common.p_value")]
    values = [format_statistic_apa(w_stat), format_p_apa(p_val)]
    headers += [t("verbal.col_significant")] * (1 if cfg.verbal_indicators else 0)
    values += [significance_verbal(p_val)] * (1 if cfg.verbal_indicators else 0)
    headers += ["r<sub>rb</sub>"] * (1 if cfg.effect_size else 0)
    values += [format_statistic_apa(rbc)] * (1 if cfg.effect_size else 0)
    headers += [t("effect.col.magnitude")] * show_verbal
    values += [correlation_magnitude(rbc)] * show_verbal

    if cfg.effect_size:
        test_result = TestResult(variable="", letter=["W", "r<sub>rb</sub>"], statistic=[w_stat, rbc], p=p_val)
    else:
        test_result = TestResult(variable="", letter="W", statistic=w_stat, p=p_val)

    result.update_and_add_element(
        _result_table(t("paired.caption.wilcoxon"), headers, values, test_result, t("paired.test.wilcoxon"), p_val),
        "paired omnibus",
    )


def _rm_anova(result, wide, conditions, cfg):
    show_verbal = 1 if (cfg.effect_size and cfg.verbal_indicators) else 0
    long = _to_long(wide, conditions)
    aov = pg.rm_anova(data=long, dv=_VALUE, within=_CONDITION, subject=_SUBJECT, correction=True, detailed=False)
    f_stat = aov["F"].values[0]
    p_val = aov["p-unc"].values[0]
    df1 = aov["ddof1"].values[0]
    df2 = aov["ddof2"].values[0]
    ng2 = aov["ng2"].values[0]
    p_gg = aov["p-GG-corr"].values[0]
    eps = aov["eps"].values[0]

    headers = ["F", "df1", "df2", t("common.p_value")]
    values = [format_statistic_apa(f_stat), str(df1), str(df2), format_p_apa(p_val)]
    headers += [t("verbal.col_significant")] * (1 if cfg.verbal_indicators else 0)
    values += [significance_verbal(p_val)] * (1 if cfg.verbal_indicators else 0)
    headers += ["&eta;&sup2;<sub>G</sub>"] * (1 if cfg.effect_size else 0)
    values += [format_statistic_apa(ng2)] * (1 if cfg.effect_size else 0)
    headers += [t("effect.col.magnitude")] * show_verbal
    values += [_eta_squared_magnitude(ng2)] * show_verbal

    if cfg.effect_size:
        test_result = TestResult(
            variable="", letter=["F", "&eta;&sup2;<sub>G</sub>"], statistic=[f_stat, ng2], p=p_val, df=df1, df2=df2
        )
    else:
        test_result = TestResult(variable="", letter="F", statistic=f_stat, p=p_val, df=df1, df2=df2)

    table = _result_table(
        t("paired.caption.rm_anova"), headers, values, test_result, t("paired.test.rm_anova"), p_val
    )
    table.table_note = t("paired.note.gg", p=format_p_apa_full(p_gg), eps=format_value_apa(eps))
    result.update_and_add_element(table, "paired omnibus")

    if cfg.effect_size and p_val < 0.05:
        pairwise = pg.pairwise_tests(
            data=long, dv=_VALUE, within=_CONDITION, subject=_SUBJECT, padjust="holm", parametric=True
        )
        pair_p = {frozenset((row["A"], row["B"])): row["p-corr"] for _, row in pairwise.iterrows()}
        result.update_and_add_element(
            _posthoc_table(
                conditions,
                lambda i, j: pair_p[frozenset((conditions[i], conditions[j]))],
                t("paired.caption.posthoc_param"),
                t("paired.posthoc.pairwise_t"),
            ),
            "paired posthoc",
        )


def _friedman(result, wide, conditions, cfg):
    show_verbal = 1 if (cfg.effect_size and cfg.verbal_indicators) else 0
    chi2, p_val = stats.friedmanchisquare(*[wide[col] for col in conditions])
    df = len(conditions) - 1
    kendall_w = chi2 / (len(wide) * (len(conditions) - 1))

    headers = ["&chi;&sup2;", "df", t("common.p_value")]
    values = [format_statistic_apa(chi2), str(df), format_p_apa(p_val)]
    headers += [t("verbal.col_significant")] * (1 if cfg.verbal_indicators else 0)
    values += [significance_verbal(p_val)] * (1 if cfg.verbal_indicators else 0)
    headers += ["W"] * (1 if cfg.effect_size else 0)
    values += [format_statistic_apa(kendall_w)] * (1 if cfg.effect_size else 0)
    headers += [t("effect.col.magnitude")] * show_verbal
    values += [_kendall_w_magnitude(kendall_w)] * show_verbal

    if cfg.effect_size:
        test_result = TestResult(variable="", letter=["&chi;&sup2;", "W"], statistic=[chi2, kendall_w], p=p_val, df=df)
    else:
        test_result = TestResult(variable="", letter="&chi;&sup2;", statistic=chi2, p=p_val, df=df)

    result.update_and_add_element(
        _result_table(t("paired.caption.friedman"), headers, values, test_result, t("paired.test.friedman"), p_val),
        "paired omnibus",
    )

    if cfg.effect_size and p_val < 0.05:
        matrix = posthoc_nemenyi_friedman(wide[list(conditions)].to_numpy())
        result.update_and_add_element(
            _posthoc_table(
                conditions,
                lambda i, j: matrix.iloc[i, j],
                t("paired.caption.posthoc_nonparam"),
                t("paired.posthoc.nemenyi"),
            ),
            "paired posthoc",
        )


def _posthoc_table(conditions, get_p, caption, test_name) -> HTMLTableV2:
    """Lower-triangular matrix of pairwise p-values, plus a sentence listing the
    significant pairs (mirrors the t-test/ANOVA post-hoc tables)."""
    table = HTMLTableV2(table_caption=caption)
    table.add_single_row_apa(
        Row([Cell()] + [Cell(t("common.p_value"), col_span=len(conditions), center=True, border_bottom=True)])
    )
    table.add_title_row_apa(Row([Cell()] + [Cell(name, center=True) for name in conditions]))

    significant = []
    for i, name in enumerate(conditions):
        row = [Cell(name, push_to_left=True)]
        for j in range(i + 1):
            if i == j:
                row.append(Cell(MDASH, center=True))
            else:
                p_val = get_p(i, j)
                row.append(Cell(format_p_apa(p_val), center=True))
                if p_val < 0.05:
                    significant.append((i, j))
        table.add_single_row_apa(Row(row))

    table.add_text(
        t(
            "paired.posthoc_sentence",
            name=test_name,
            groups=smart_comma_join(
                [
                    t("ttest.group_pair", a=conditions[i], b=conditions[j], p=format_p_apa_full(get_p(i, j)))
                    for i, j in significant
                ]
            ),
        )
    )
    return table


def _add_plots(result, wide, conditions):
    box_plot = create_box_plot(
        groups=[wide[col] for col in conditions],
        group_names=list(conditions),
        column=t("paired.plot.value_axis"),
        grouping_column=t("paired.plot.condition_axis"),
    )
    result.update_and_add_element(box_plot, "paired box_plot")


def _eta_squared_magnitude(eta_sq) -> str:
    """Eta-squared bands: .01 small, .06 medium, .14 large (Cohen)."""
    if eta_sq < 0.01:
        return t("effect.magnitude.negligible")
    if eta_sq < 0.06:
        return t("effect.magnitude.small")
    if eta_sq < 0.14:
        return t("effect.magnitude.medium")
    return t("effect.magnitude.large")


def _kendall_w_magnitude(w) -> str:
    """Kendall's W agreement bands: .1 small, .3 moderate, .5 large."""
    if w < 0.1:
        return t("effect.magnitude.negligible")
    if w < 0.3:
        return t("effect.magnitude.small")
    if w < 0.5:
        return t("effect.magnitude.medium")
    return t("effect.magnitude.large")
