#  Copyright (c) 2023 StatPrism Team. All rights reserved.


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


def get_report(columns, correlation_matrix, p_matrix, df_matrix, report_non_significant, kind: CorrelationType):
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
        stats = format_apa(r, p, df, letter)
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
            stats = format_apa(r, p, df, letter)
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
