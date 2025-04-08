#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

from typing import cast

import pandas as pd
from scipy import stats
from scipy.stats._morestats import LeveneResult

from src.common.result.classes.html_result import Cell, HTMLTableV2, Row
from src.common.utility import format_p_apa, format_statistic_apa
from src.common.verbal.test import TestResult, describe_single_test_multiple_variables


def process_homogeneity_check(
    df: pd.DataFrame,
    selected_columns,
    grouping_column,
):
    table = HTMLTableV2(table_caption="Levene's test for homogeneity of variance")
    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell("Levene's F", center=True),
                Cell("p-value", center=True),
            ]
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
            test_name="Levene's test",
            test_check="homogeneity of variance",
            yes_columns=homogeneous_columns_classes,
            no_columns=non_homogeneous_columns_classes,
            yes_property="have homogeneity of variance",
            no_property="have inhomogeneous variance",
        )
    )

    return homogeneous_columns, non_homogeneous_columns, table
