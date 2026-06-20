#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import pandas as pd

from src.common.translations import t
from src.side_area_panel.modules.common.utility import format_apa, smart_comma_join
from src.side_area_panel.modules.correlation.correlation_result import CorrelationType

_NAME_KEY = {
    CorrelationType.PEARSON: "correlation.name.pearson",
    CorrelationType.SPEARMAN: "correlation.name.spearman",
    CorrelationType.KENDALL: "correlation.name.kendall",
    CorrelationType.PHI: "correlation.name.phi",
    CorrelationType.TETRACHORIC: "correlation.name.tetrachoric",
    CorrelationType.POLYCHORIC: "correlation.name.polychoric",
}
_LETTER = {
    CorrelationType.PEARSON: "r",
    CorrelationType.SPEARMAN: "ρ",
    CorrelationType.KENDALL: "τ",
    CorrelationType.PHI: "φ",
    CorrelationType.TETRACHORIC: "ρ<sub>t</sub>",
    CorrelationType.POLYCHORIC: "ρ<sub>pc</sub>",
}

# Kendall's tau-c is an optional variant that may not exist in every build.
if hasattr(CorrelationType, "KENDALL_C"):
    _NAME_KEY[CorrelationType.KENDALL_C] = "correlation.name.kendall_c"
    _LETTER[CorrelationType.KENDALL_C] = "τ<sub>c</sub>"


def _strength(r):
    a = abs(round(r, 2))
    if a > 0.5:
        return t("correlation.strength.strong")
    if a > 0.3:
        return t("correlation.strength.moderate")
    if a > 0.1:
        return t("correlation.strength.weak")
    return t("correlation.strength.very_weak")


def _sign(r):
    return t("correlation.sign.positive") if r > 0 else t("correlation.sign.negative")


def _with_ci(stats: str, ci_matrix, row, column) -> str:
    """Append the CI string to an APA stats fragment when a CI is available."""
    if ci_matrix is None:
        return stats
    ci = ci_matrix.loc[row, column]
    if isinstance(ci, str) and ci:
        return f"{stats}, {t('common.ci_95')} {ci}"
    return stats


def get_report(columns, correlation_matrix, p_matrix, df_matrix, report_non_significant, kind: CorrelationType, ci_matrix=None):
    if kind not in _NAME_KEY:
        raise ValueError(f"Unknown correlation type: {kind}")
    name = t(_NAME_KEY[kind])
    letter = _LETTER[kind]

    variables = smart_comma_join([f"«{var}»" for var in columns])
    text = t("correlation.report.intro", name=name, vars=variables)

    if len(columns) == 2:
        r = correlation_matrix.loc[columns[1], columns[0]]
        p = p_matrix.loc[columns[1], columns[0]]
        df = df_matrix.loc[columns[1], columns[0]]
        stats = _with_ci(format_apa(r, p, df, letter), ci_matrix, columns[1], columns[0])
        if p > 0.05:
            return text + t("correlation.report.two_nonsignificant", stats=stats)
        text += t("correlation.report.two_significant", strength=_strength(r), sign=_sign(r), stats=stats)
        if abs(r) < 0.1:
            text += t("correlation.report.negligible")
        return text

    if p_matrix.min().min() > 0.05 and not report_non_significant:
        return t("correlation.report.none_significant")

    for i_row, row in enumerate(columns):
        for i_column, column in enumerate(columns):
            if i_column >= i_row:
                continue
            r = correlation_matrix.loc[row, column]
            p = p_matrix.loc[row, column]
            df = df_matrix.loc[row, column]
            if round(p, 3) > 0.05 and not report_non_significant:
                continue
            stats = _with_ci(format_apa(r, p, df, letter), ci_matrix, row, column)
            if p > 0.05:
                text += t("correlation.report.multi_nonsignificant", var1=row, var2=column, stats=stats)
            else:
                text += t(
                    "correlation.report.multi_significant",
                    strength=_strength(r),
                    sign=_sign(r),
                    var1=row,
                    var2=column,
                    stats=stats,
                )
                if abs(r) < 0.1:
                    text += t("correlation.report.negligible")
    return text


def get_cross_report(rows, cols, correlation_matrix, p_matrix, df_matrix, report_non_significant, kind: CorrelationType, ci_matrix=None):
    """Verbal summary for a rectangular two-set correlation: every (row, col) pair, skipping
    a variable paired with itself when it appears in both sets."""
    if kind not in _NAME_KEY:
        raise ValueError(f"Unknown correlation type: {kind}")
    name = t(_NAME_KEY[kind])
    letter = _LETTER[kind]

    row_vars = smart_comma_join([f"«{var}»" for var in rows])
    col_vars = smart_comma_join([f"«{var}»" for var in cols])
    text = t("correlation.report.cross_intro", name=name, rows=row_vars, cols=col_vars)

    reported_any = False
    for row in rows:
        for col in cols:
            if row == col:
                continue
            r = correlation_matrix.loc[row, col]
            p = p_matrix.loc[row, col]
            df = df_matrix.loc[row, col]
            if p is None or pd.isna(p):
                continue
            if round(p, 3) > 0.05 and not report_non_significant:
                continue
            reported_any = True
            stats = _with_ci(format_apa(r, p, df, letter), ci_matrix, row, col)
            if p > 0.05:
                text += t("correlation.report.multi_nonsignificant", var1=row, var2=col, stats=stats)
            else:
                text += t(
                    "correlation.report.multi_significant",
                    strength=_strength(r),
                    sign=_sign(r),
                    var1=row,
                    var2=col,
                    stats=stats,
                )
                if abs(r) < 0.1:
                    text += t("correlation.report.negligible")

    if not reported_any and not report_non_significant:
        return t("correlation.report.none_significant")
    return text
