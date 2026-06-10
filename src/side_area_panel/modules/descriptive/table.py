#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import Any, Dict, List

import pandas as pd

from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.utility import format_p_apa_exact, format_r_apa


def get_descriptive_table_no_groupby(
    df: pd.DataFrame,
    caption: str,
    note: str = "",
) -> HTMLTableV2:
    table = HTMLTableV2(table_caption=caption)

    # Add header1
    table.add_single_row_apa(
        Row([Cell()] + [Cell() for _ in range(6)] + [Cell("Shapiro-Wilk", col_span=2, center=True, border_bottom=True)])
    )

    # Add header2
    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell("N", center=True),
                Cell("Missing", center=True),
                Cell("Mean", center=True),
                Cell("SD", center=True),
                Cell("Min", center=True),
                Cell("Max", center=True),
                Cell("W", center=True),
                Cell("p", center=True),
            ]
        )
    )

    # Add matrix
    for i_row, row in enumerate(df.index):
        table.add_single_row_apa(
            Row(
                [
                    Cell(df.loc[row, "variable"], center=True),
                    Cell(f'{int(df.loc[row, "N"])}', center=True),
                    Cell(f'{int(df.loc[row, "missing"])}', center=True),
                    Cell(f'{df.loc[row, "mean"]}', center=True),
                    Cell(f'{df.loc[row, "std"]}', center=True),
                    Cell(f'{df.loc[row, "min"]}', center=True),
                    Cell(f'{df.loc[row, "max"]}', center=True),
                    Cell(format_r_apa(df.loc[row, "shapiro_wilk_w"], decimals=3), center=True),
                    Cell(format_p_apa_exact(df.loc[row, "shapiro_wilk_p"]), center=True),
                ]
            )
        )

    table.table_note = note

    return table


def get_descriptive_table_groupby(
    data: List[Dict[str, Any]],
    groupby_column: str,
    groupby_values: List[str],
    caption: str,
    note: str = "",
) -> HTMLTableV2:
    table = HTMLTableV2(table_caption=caption)

    # Add header1
    table.add_single_row_apa(
        Row(
            [Cell(), Cell()]
            + [Cell() for _ in range(6)]
            + [Cell("Shapiro-Wilk", col_span=2, center=True, border_bottom=True)]
        )
    )

    # Add header2
    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell(groupby_column, center=True),
                Cell("N", center=True),
                Cell("Missing", center=True),
                Cell("Mean", center=True),
                Cell("SD", center=True),
                Cell("Min", center=True),
                Cell("Max", center=True),
                Cell("W", center=True),
                Cell("p", center=True),
            ]
        )
    )

    # Add matrix
    for row in data:
        for i, groupby_value in enumerate(groupby_values):
            if groupby_value not in row:
                continue
            table.add_single_row_apa(
                Row(
                    [
                        Cell(row[groupby_value]["variable"], push_to_left=True) if i == 0 else Cell(),
                        Cell(groupby_value, center=True),
                        Cell(f'{int(row[groupby_value]["N"])}', center=True),
                        Cell(f'{int(row[groupby_value]["missing"])}', center=True),
                        Cell(f'{row[groupby_value]["mean"]}', center=True),
                        Cell(f'{row[groupby_value]["std"]}', center=True),
                        Cell(f'{row[groupby_value]["min"]}', center=True),
                        Cell(f'{row[groupby_value]["max"]}', center=True),
                        Cell(format_r_apa(row[groupby_value]["shapiro_wilk_w"], decimals=3), center=True),
                        Cell(format_p_apa_exact(row[groupby_value]["shapiro_wilk_p"]), center=True),
                    ]
                )
            )

    table.table_note = note

    return table
