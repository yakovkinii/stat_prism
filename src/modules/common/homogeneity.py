from typing import cast

import pandas as pd
from scipy import stats
from scipy.stats._morestats import LeveneResult

from src.common.result.classes.html_result import Cell, HTMLTable, HTMLText, Row
from src.common.utility import format_p_apa, format_statistic_apa
from src.common.verbal.test import describe_test


def process_homogeneity_check(
    df: pd.DataFrame,
    selected_columns,
    grouping_column,
):
    table = HTMLTable([])
    table.table_caption = "Levene's test for homogeneity of variance"
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

    for index, col in enumerate(selected_columns):
        levene_result = cast(
            LeveneResult,
            stats.levene(*[group[col].dropna() for name, group in df.groupby(grouping_column)]),
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
        else:
            homogeneous_columns.append(col)

    text = HTMLText(
        describe_test(
            test_name="Levene's test",
            yes_columns=homogeneous_columns,
            no_columns=non_homogeneous_columns,
            yes_property="have homogeneity of variance",
            no_property="do not have homogeneity of variance",
        )
    )

    return homogeneous_columns, non_homogeneous_columns, table, text
