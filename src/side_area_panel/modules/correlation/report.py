#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.


import pandas as pd

from src.common.translations import t
from src.side_area_panel.modules.common.prose import prose_includes
from src.side_area_panel.modules.common.utility import format_apa, smart_comma_join
from src.side_area_panel.modules.common.verbal.compact import ReportItem, summarize
from src.side_area_panel.modules.correlation.correlation_result import CorrelationType


def _significant(p) -> bool:
    return round(p, 3) <= 0.05


def _notable(r, p) -> bool:
    """A "key finding": significant and strong (|r| > 0.5, matching ``_strength``)."""
    return _significant(p) and abs(round(r, 2)) > 0.5


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
    CorrelationType.SPEARMAN: "&rho;",
    CorrelationType.KENDALL: "&tau;",
    CorrelationType.PHI: "&phi;",
    CorrelationType.TETRACHORIC: "&rho;<sub>t</sub>",
    CorrelationType.POLYCHORIC: "&rho;<sub>pc</sub>",
}

# Kendall's tau-c is an optional variant that may not exist in every build.
if hasattr(CorrelationType, "KENDALL_C"):
    _NAME_KEY[CorrelationType.KENDALL_C] = "correlation.name.kendall_c"
    _LETTER[CorrelationType.KENDALL_C] = "&tau;<sub>c</sub>"


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


def _strength_nom(r):
    """Nominative strength word for the compacter's parenthetical descriptor."""
    a = abs(round(r, 2))
    if a > 0.5:
        key = "strong"
    elif a > 0.3:
        key = "moderate"
    elif a > 0.1:
        key = "weak"
    else:
        key = "very_weak"
    return t(f"correlation.strength_nom.{key}")


def _descriptor(r):
    direction = t("correlation.dir.direct") if r > 0 else t("correlation.dir.inverse")
    return t("correlation.descriptor", strength=_strength_nom(r), sign=direction)


def _pair_label(a, b):
    return f"&laquo;{a}&raquo;&ndash;&laquo;{b}&raquo;"


_NOUN = ("verbal.noun.correlations.nom", "verbal.noun.correlations.gen")


def _summarize(items, detail):
    return summarize(
        items,
        detail,
        noun_nom=t(_NOUN[0]),
        noun_gen=t(_NOUN[1]),
        notable_one_key="correlation.compact.most_notable_one",
        notable_key="correlation.compact.most_notable",
    )


def _with_ci(stats: str, ci_matrix, row, column) -> str:
    """Append the CI string to an APA stats fragment when a CI is available."""
    if ci_matrix is None:
        return stats
    ci = ci_matrix.loc[row, column]
    if isinstance(ci, str) and ci:
        return f"{stats}, {t('common.ci_95')} {ci}"
    return stats


def get_report(columns, correlation_matrix, p_matrix, df_matrix, detail, kind: CorrelationType, ci_matrix=None):
    if kind not in _NAME_KEY:
        raise ValueError(f"Unknown correlation type: {kind}")
    name = t(_NAME_KEY[kind])
    letter = _LETTER[kind]

    variables = smart_comma_join([f"&laquo;{var}&raquo;" for var in columns])
    text = t("correlation.report.intro", name=name, vars=variables)

    if len(columns) == 2:
        r = correlation_matrix.loc[columns[1], columns[0]]
        p = p_matrix.loc[columns[1], columns[0]]
        df = df_matrix.loc[columns[1], columns[0]]
        if not prose_includes(detail, _significant(p), _notable(r, p)):
            return t("correlation.report.none_significant")
        stats = _with_ci(format_apa(r, p, df, letter), ci_matrix, columns[1], columns[0])
        if p > 0.05:
            return text + t("correlation.report.two_nonsignificant", stats=stats)
        text += t("correlation.report.two_significant", strength=_strength(r), sign=_sign(r), stats=stats)
        if abs(r) < 0.1:
            text += t("correlation.report.negligible")
        return text

    items = []
    for i_row, row in enumerate(columns):
        for i_column, column in enumerate(columns):
            if i_column >= i_row:
                continue
            r = correlation_matrix.loc[row, column]
            p = p_matrix.loc[row, column]
            df = df_matrix.loc[row, column]
            if p is None or pd.isna(p):
                continue
            items.append(
                ReportItem(
                    label=_pair_label(column, row),
                    significant=_significant(p),
                    apa=_with_ci(format_apa(r, p, df, letter), ci_matrix, row, column),
                    magnitude=abs(r),
                    notable=_notable(r, p),
                    descriptor=_descriptor(r),
                )
            )
    return text + _summarize(items, detail)


def get_cross_report(
    rows, cols, correlation_matrix, p_matrix, df_matrix, detail, kind: CorrelationType, ci_matrix=None
):
    """Verbal summary for a rectangular two-set correlation: every (row, col) pair, skipping
    a variable paired with itself when it appears in both sets."""
    if kind not in _NAME_KEY:
        raise ValueError(f"Unknown correlation type: {kind}")
    name = t(_NAME_KEY[kind])
    letter = _LETTER[kind]

    row_vars = smart_comma_join([f"&laquo;{var}&raquo;" for var in rows])
    col_vars = smart_comma_join([f"&laquo;{var}&raquo;" for var in cols])
    text = t("correlation.report.cross_intro", name=name, rows=row_vars, cols=col_vars)

    items = []
    for row in rows:
        for col in cols:
            if row == col:
                continue
            r = correlation_matrix.loc[row, col]
            p = p_matrix.loc[row, col]
            df = df_matrix.loc[row, col]
            if p is None or pd.isna(p):
                continue
            items.append(
                ReportItem(
                    label=_pair_label(row, col),
                    significant=_significant(p),
                    apa=_with_ci(format_apa(r, p, df, letter), ci_matrix, row, col),
                    magnitude=abs(r),
                    notable=_notable(r, p),
                    descriptor=_descriptor(r),
                )
            )
    return text + _summarize(items, detail)
