#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import List

import numpy as np
import pandas as pd

from src.common.translations import t
from src.side_area_panel.modules.common.column_numbering import ColumnNumbering
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.utility import (
    format_p_apa_exact,
    format_p_apa_prose,
    format_r_apa,
    format_value_apa,
)

# Extended numeric columns, in display order: (header label, stat-dict key, decimals).
_EXTENDED_COLUMNS = [
    ("SE", "se", 2),
    ("Median", "median", 2),
    ("Q1", "q1", 2),
    ("Q3", "q3", 2),
    ("Skew", "skew", 2),
    ("Kurt", "kurtosis", 2),
]


def _numbering(numbering):
    """Use the given numbering, or a disabled pass-through one when None."""
    return numbering if numbering is not None else ColumnNumbering([], False)


def get_numeric_summary_table(
    rows: List[dict],
    caption: str,
    extended: bool = False,
    groupby_column: str = None,
    numbering=None,
) -> HTMLTableV2:
    """Numeric summary. `rows` is a flat list of per-variable (or per-variable-per-group)
    stat dicts. With a groupby_column the variable name is shown once per block."""
    numbering = _numbering(numbering)
    table = HTMLTableV2(table_caption=caption)
    grouped = groupby_column is not None

    header = [Cell()]
    if grouped:
        header.append(Cell(groupby_column, center=True))
    header += [Cell("N", center=True), Cell("Missing", center=True), Cell("Mean", center=True), Cell("SD", center=True)]
    if extended:
        header += [Cell(label, center=True) for label, _, _ in _EXTENDED_COLUMNS]
    header += [Cell("Min", center=True), Cell("Max", center=True)]
    table.add_title_row_apa(Row(header))

    prev_variable = None
    for r in rows:
        label = numbering.label(r["variable"]) if r["variable"] != prev_variable else ""
        cells = [Cell(label, push_to_left=True)]
        prev_variable = r["variable"]
        if grouped:
            cells.append(Cell(str(r.get("group", "")), center=True))
        cells += [
            Cell(str(int(r["N"])), center=True),
            Cell(str(int(r["missing"])), center=True),
            Cell(format_value_apa(r["mean"], 2), center=True),
            Cell(format_value_apa(r["std"], 2), center=True),
        ]
        if extended:
            cells += [Cell(format_value_apa(r[key], dec), center=True) for _, key, dec in _EXTENDED_COLUMNS]
        cells += [
            Cell(format_value_apa(r["min"], 2), center=True),
            Cell(format_value_apa(r["max"], 2), center=True),
        ]
        table.add_single_row_apa(Row(cells))

    table.table_note = numbering.append_to_note(table.table_note or "")
    return table


def _variable_label(variable, group):
    return f"{variable} ({group})" if group is not None else str(variable)


def get_normality_table(
    rows: List[dict],
    caption: str,
    test_name: str,
    statistic_letter: str,
    groupby_column: str = None,
    show_normal_column: bool = True,
    show_report: bool = True,
    numbering=None,
) -> HTMLTableV2:
    """Normality results: per variable (or per group) the test statistic, p, and (when
    `show_normal_column`) an in-table verbal normal? conclusion. When `show_report`, a
    plain-language summary (prose) follows the table. `rows` have keys: variable, group,
    norm_stat, norm_p."""
    numbering = _numbering(numbering)
    table = HTMLTableV2(table_caption=caption)
    grouped = groupby_column is not None

    header = [Cell()]
    if grouped:
        header.append(Cell(groupby_column, center=True))
    header += [
        Cell(statistic_letter, center=True),
        Cell(t("common.p_value"), center=True),
    ]
    if show_normal_column:
        header.append(Cell(t("descriptive.normality.col_normal"), center=True))
    table.add_title_row_apa(Row(header))

    prev_variable = None
    for r in rows:
        is_normal = (r["norm_p"] is not None) and (not np.isnan(r["norm_p"])) and (r["norm_p"] > 0.05)
        normal_text = (
            t("descriptive.normality.yes")
            if is_normal
            else (t("descriptive.normality.no") if not _is_nan(r["norm_p"]) else "—")
        )
        label = numbering.label(r["variable"]) if r["variable"] != prev_variable else ""
        cells = [Cell(label, push_to_left=True)]
        prev_variable = r["variable"]
        if grouped:
            cells.append(Cell(str(r.get("group", "")), center=True))
        cells += [
            Cell(format_r_apa(r["norm_stat"], 3), center=True),
            Cell(format_p_apa_exact(r["norm_p"]), center=True),
        ]
        if show_normal_column:
            cells.append(Cell(normal_text, center=True))
        table.add_single_row_apa(Row(cells))

    show_report and table.add_text(_normality_report(rows, test_name, statistic_letter))
    # If any cell is blank (test could not run), explain why rather than leaving it unexplained.
    if any(_is_nan(r["norm_p"]) for r in rows):
        table.add_text(t("descriptive.normality.note_blank"))
    table.table_note = numbering.append_to_note(table.table_note or "")
    return table


def _is_nan(value):
    return value is None or (isinstance(value, float) and np.isnan(value))


def _normality_report(rows, test_name, statistic_letter) -> str:
    text = t("descriptive.normality.intro", test=test_name)
    for r in rows:
        if _is_nan(r["norm_p"]):
            continue
        stats_str = f"{statistic_letter} = {format_r_apa(r['norm_stat'], 3)}, {format_p_apa_prose(r['norm_p'])}"
        key = "descriptive.normality.normal" if r["norm_p"] > 0.05 else "descriptive.normality.not_normal"
        text += t(key, var=_variable_label(r["variable"], r.get("group")), stats=stats_str)
    return text


def get_frequency_table(caption: str, value_counts: pd.Series) -> HTMLTableV2:
    """Frequency table for a categorical variable: each category's count and percentage
    of non-missing observations, plus a total row."""
    table = HTMLTableV2(table_caption=caption)
    total = int(value_counts.sum())

    table.add_title_row_apa(
        Row(
            [
                Cell(t("descriptive.freq.category"), push_to_left=True),
                Cell(t("descriptive.freq.count"), center=True),
                Cell(t("descriptive.freq.percent"), center=True),
            ]
        )
    )
    for category, count in value_counts.items():
        count = int(count)
        pct = (100.0 * count / total) if total else 0.0
        table.add_single_row_apa(
            Row(
                [
                    Cell(str(category), push_to_left=True),
                    Cell(str(count), center=True),
                    Cell(format_value_apa(pct, 1), center=True),
                ]
            )
        )
    table.add_single_row_apa(
        Row(
            [
                Cell(t("descriptive.freq.total"), push_to_left=True),
                Cell(str(total), center=True),
                Cell(format_value_apa(100.0 if total else 0.0, 1), center=True),
            ]
        )
    )
    return table


def get_grouped_frequency_table(caption: str, groupby_column: str, col: str, group_counts, verbal=False) -> HTMLTableV2:
    """Frequency table split by a grouping column. `group_counts` is a list of
    (group_value, value_counts Series). Each block lists that group's category counts and
    within-group percentages; the group label is shown once per block. A verbal summary
    of each group's modal category follows."""
    table = HTMLTableV2(table_caption=caption)
    table.add_title_row_apa(
        Row(
            [
                Cell(groupby_column, push_to_left=True),
                Cell(t("descriptive.freq.category"), push_to_left=True),
                Cell(t("descriptive.freq.count"), center=True),
                Cell(t("descriptive.freq.percent"), center=True),
            ]
        )
    )
    for group_value, value_counts in group_counts:
        group_total = int(value_counts.sum())
        first = True
        for category, count in value_counts.items():
            count = int(count)
            pct = (100.0 * count / group_total) if group_total else 0.0
            table.add_single_row_apa(
                Row(
                    [
                        Cell(str(group_value) if first else "", push_to_left=True),
                        Cell(str(category), push_to_left=True),
                        Cell(str(count), center=True),
                        Cell(format_value_apa(pct, 1), center=True),
                    ]
                )
            )
            first = False

    if verbal:
        table.add_text(_grouped_frequency_report(col, group_counts))
    return table


def _grouped_frequency_report(col, group_counts) -> str:
    """One sentence per group naming its most common category."""
    text = ""
    for group_value, value_counts in group_counts:
        if value_counts.empty:
            continue
        group_total = int(value_counts.sum())
        top_category = value_counts.idxmax()
        top_count = int(value_counts.max())
        pct = (100.0 * top_count / group_total) if group_total else 0.0
        text += t(
            "descriptive.freq.group_line",
            group=group_value,
            col=col,
            category=top_category,
            pct=format_value_apa(pct, 1),
            n=group_total,
        )
    return text
