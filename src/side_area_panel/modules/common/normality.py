#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import cast

import pandas as pd
from scipy import stats
from scipy.stats._morestats import ShapiroResult

from src.common.translations import t
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.utility import (
    format_p_apa,
    format_statistic_apa,
)
from src.side_area_panel.modules.common.verbal.significance import assumption_met_verbal
from src.side_area_panel.modules.common.verbal.test import (
    TestResult,
    describe_single_test_multiple_variables,
)


def process_normality_check(
    df: pd.DataFrame,
    selected_columns,
    grouping_column,
    verbal_indicators=False,
):
    show_verbal = 1 if verbal_indicators else 0
    table = HTMLTableV2(table_caption=t("ttest.caption.shapiro"))
    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell(grouping_column, center=True),
                Cell(t("ttest.col.shapiro_w"), center=True),
                Cell(t("common.p_value"), center=True),
            ]
            + [Cell(t("descriptive.normality.col_normal"), center=True)] * show_verbal
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
                    + [Cell(assumption_met_verbal(shapiro_result.pvalue), center=True)] * show_verbal
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
            test_name=t("ttest.test.shapiro"),
            test_check=t("ttest.check.normality"),
            yes_columns=normal_columns_classes,
            no_columns=non_normal_columns_classes,
            yes_property=t("ttest.prop.normal"),
            no_property=t("ttest.prop.not_normal"),
        )
    )

    return normal_columns, non_normal_columns, table
