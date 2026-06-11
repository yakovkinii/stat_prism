#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import cast

import pandas as pd
from scipy import stats
from scipy.stats._morestats import LeveneResult

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


def process_homogeneity_check(
    df: pd.DataFrame,
    selected_columns,
    grouping_column,
    verbal_indicators=False,
):
    show_verbal = 1 if verbal_indicators else 0
    table = HTMLTableV2(table_caption=t("ttest.caption.levene"))
    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell(t("ttest.col.levene_f"), center=True),
                Cell(t("common.p_value"), center=True),
            ]
            + [Cell(t("verbal.col_equal_var"), center=True)] * show_verbal
        )
    )

    non_homogeneous_columns = []
    homogeneous_columns = []
    non_homogeneous_columns_classes = []
    homogeneous_columns_classes = []

    for index, col in enumerate(selected_columns):
        levene_result = cast(
            LeveneResult,
            stats.levene(*[group[col].dropna() for name, group in df.groupby(grouping_column)], center="mean"),
        )

        table.add_single_row_apa(
            Row(
                [
                    Cell(col, push_to_left=True),
                    Cell(format_statistic_apa(levene_result.statistic), center=True),
                    Cell(format_p_apa(levene_result.pvalue), center=True),
                ]
                + [Cell(assumption_met_verbal(levene_result.pvalue), center=True)] * show_verbal
            )
        )
        if levene_result.pvalue <= 0.05:
            non_homogeneous_columns.append(col)
            non_homogeneous_columns_classes.append(
                TestResult(
                    variable=col,
                    letter="F",
                    statistic=levene_result.statistic,
                    p=levene_result.pvalue,
                )
            )
        else:
            homogeneous_columns.append(col)
            homogeneous_columns_classes.append(
                TestResult(
                    variable=col,
                    letter="F",
                    statistic=levene_result.statistic,
                    p=levene_result.pvalue,
                )
            )

    table.add_text(
        describe_single_test_multiple_variables(
            test_name=t("ttest.test.levene"),
            test_check=t("ttest.check.homogeneity"),
            yes_columns=homogeneous_columns_classes,
            no_columns=non_homogeneous_columns_classes,
            yes_property=t("ttest.prop.homogeneous"),
            no_property=t("ttest.prop.inhomogeneous"),
        )
    )

    return homogeneous_columns, non_homogeneous_columns, table
