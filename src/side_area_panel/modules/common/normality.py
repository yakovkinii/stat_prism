#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import cast

import pandas as pd
from scipy import stats
from scipy.stats._morestats import ShapiroResult

from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.utility import (
    format_p_apa,
    format_statistic_apa,
)
from src.side_area_panel.modules.common.verbal.test import (
    TestResult,
    describe_single_test_multiple_variables,
)


def process_normality_check(
    df: pd.DataFrame,
    selected_columns,
    grouping_column,
):
    table = HTMLTableV2(table_caption="Shapiro-Wilk normality test")
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

    non_normal_columns_classes = []
    normal_columns_classes = []

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
            normal_columns_classes.append(TestResult(variable=col, letter=[], statistic=[]))
        else:
            non_normal_columns.append(col)
            non_normal_columns_classes.append(TestResult(variable=col, letter=[], statistic=[]))

    table.add_text(
        describe_single_test_multiple_variables(
            test_name="Shapiro-Wilk test",
            test_check="normality within groups",
            yes_columns=normal_columns_classes,
            no_columns=non_normal_columns_classes,
            yes_property="are normally distributed (p > 0.05)",
            no_property="are not normally distributed (p < 0.05)",
        )
    )

    return normal_columns, non_normal_columns, table
