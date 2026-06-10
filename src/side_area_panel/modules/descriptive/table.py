#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import List

import pandas as pd

from src.common.translations import t
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.utility import (
    format_p_apa_exact,
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


def get_numeric_summary_table(
    rows: List[dict],
    caption: str,
    extended: bool = False,
    groupby_column: str = None,
) -> HTMLTableV2:
    """Numeric summary. `rows` is a flat list of per-variable (or per-variable-per-group)
    stat dicts. With a groupby_column the variable name is shown once per block."""
    table = HTMLTableV2(table_caption=caption)
    grouped = groupby_column is not None

    # leading (non Shapiro-Wilk) columns: variable [+ group] + N, Missing, Mean, SD
    # [+ extended] + Min, Max
    n_lead = 1 + (1 if grouped else 0) + 4 + (len(_EXTENDED_COLUMNS) if extended else 0) + 2

    table.add_single_row_apa(
        Row([Cell() for _ in range(n_lead)] + [Cell("Shapiro-Wilk", col_span=2, center=True, border_bottom=True)])
    )

    header = [Cell()]
    if grouped:
        header.append(Cell(groupby_column, center=True))
    header += [Cell("N", center=True), Cell("Missing", center=True), Cell("Mean", center=True), Cell("SD", center=True)]
    if extended:
        header += [Cell(label, center=True) for label, _, _ in _EXTENDED_COLUMNS]
    header += [Cell("Min", center=True), Cell("Max", center=True), Cell("W", center=True), Cell("p", center=True)]
    table.add_title_row_apa(Row(header))

    prev_variable = None
    for r in rows:
        cells = [Cell(r["variable"] if r["variable"] != prev_variable else "", push_to_left=True)]
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
            Cell(format_r_apa(r["shapiro_w"], 3), center=True),
            Cell(format_p_apa_exact(r["shapiro_p"]), center=True),
        ]
        table.add_single_row_apa(Row(cells))

    return table


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
