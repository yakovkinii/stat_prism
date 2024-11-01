from typing import cast

import pandas as pd
from scipy import stats
from scipy.stats._morestats import ShapiroResult

from src.common.result.classes.html_result import Cell, HTMLTable, HTMLText, Row
from src.common.utility import format_p_apa, format_statistic_apa
from src.common.verbal.test import describe_test


def process_normality_check(
    df: pd.DataFrame,
    selected_columns,
    grouping_column,
):
    table = HTMLTable([])
    table.table_caption = "Shapiro-Wilk normality test"
    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell(grouping_column, center=True),
                Cell("Shapiro-Wilk W", center=True),
                Cell("p-value", center=True),
            ]
        )
    )

    non_normal_columns = []
    normal_columns = []

    for index, col in enumerate(selected_columns):
        all_normal = True
        for i, (group_name, group) in enumerate(df.groupby(grouping_column)):
            shapiro_result = cast(ShapiroResult, stats.shapiro(group[col].dropna()))
            table.add_single_row_apa(
                Row(
                    [
                        Cell(col, push_to_left=True) if i == 0 else Cell(),
                        Cell(str(group_name), center=True),
                        Cell(format_statistic_apa(shapiro_result.statistic), center=True),
                        Cell(format_p_apa(shapiro_result.pvalue), center=True),
                    ]
                )
            )
            if shapiro_result.pvalue <= 0.05:
                all_normal = False

        if all_normal:
            normal_columns.append(col)
        else:
            non_normal_columns.append(col)

    text = HTMLText(
        describe_test(
            test_name="Shapiro-Wilk test",
            yes_columns=normal_columns,
            no_columns=non_normal_columns,
            yes_property="are normally distributed",
            no_property="are not normally distributed",
        )
    )

    return normal_columns, non_normal_columns, table, text
