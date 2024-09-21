from typing import List

import pandas as pd

from src.common.result.classes.html_result import Cell, HTMLTable, Row


def format_r_apa(r, decimals=2):
    return str(f"{round(r, decimals):.{decimals}f}".replace("0.", "."))


def get_stars(p):
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return ""


def format_p_apa(p, decimals=3):
    if p < 0.001:
        return "&lt;&nbsp;.001"
    else:
        return f"{round(p, decimals):.{decimals}f}".replace("0.", ".")


EMPTY_COLUMN_NAME = "__empty__"


def get_t_test_table(
    df: pd.DataFrame,
    group_names: List[str],
    caption: str,
    note: str = None,
) -> HTMLTable:
    table = HTMLTable([])

    table.table_caption = caption

    # Add header1
    table.add_single_row_apa(
        Row(
            [Cell()]
            + [Cell(group_name, col_span=2, center=True, border_bottom=True) for group_name in group_names]
            + [Cell() for _ in range(3)]
        )
    )

    # Add header2
    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell("Mean", center=True),
                Cell("SD", center=True),
                Cell("Mean", center=True),
                Cell("SD", center=True),
                Cell("t-statistic", center=True),
                Cell("p-value", center=True),
                Cell("df", center=True),
            ]
        )
    )

    # Add matrix
    for i_row, row in enumerate(df.index):
        table.add_single_row_apa(
            Row(
                [
                    Cell(df.loc[row, "variable"], push_to_left=True),
                    Cell(f'{df.loc[row, "mean1"]:.2f}', center=True),
                    Cell(f'{df.loc[row, "std1"]:.2f}', center=True),
                    Cell(f'{df.loc[row, "mean2"]:.2f}', center=True),
                    Cell(f'{df.loc[row, "std2"]:.2f}', center=True),
                    Cell(f'{df.loc[row, "t-statistic"]:.2f}', center=True),
                    Cell(format_p_apa(df.loc[row, "p-value"]), center=True),
                    Cell(f'{int(df.loc[row, "df"])}', center=True),
                ]
            )
        )

    table.table_note = note

    return table
