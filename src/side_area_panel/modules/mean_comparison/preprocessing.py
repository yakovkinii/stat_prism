#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from __future__ import annotations

import pandas as pd

from src.data.data import Data
from src.side_area_panel.modules.mean_comparison.constant import MissingValuesInGrouping
from src.side_area_panel.modules.mean_comparison.mean_comparison_result import (
    MeanComparisonStudyConfig,
)


def prepare_df_for_mean_comparison(
    data: Data,
    cfg: MeanComparisonStudyConfig,
    map_ordinal: bool = False,
) -> pd.DataFrame:
    """
    Returns a dataframe with selected value columns + grouping column and filters applied,
    and handles missing values in the grouping column according to cfg.grouping_missing.

    Note: Value columns are left as-is here; downstream tests should dropna explicitly.
    """
    selected_columns = cfg.column_selector[0]

    grouping_column = cfg.column_selector[1][0]
    df = data.get_dataframe(
        columns=selected_columns + [grouping_column],
        map_ordinal=map_ordinal,
    ).copy()

    df.loc[
        df[grouping_column].isin(
            [
                pd.NA,
                None,
                float("nan"),
                "",
                " ",
                "NA",
                "N/A",
                "null",
                "NULL",
                "NaN",
                "nan",
            ]
        ),
        grouping_column,
    ] = pd.NA

    if cfg.grouping_missing == MissingValuesInGrouping.SKIP.value:
        df = df[df[grouping_column].notna()].copy()
    elif cfg.grouping_missing == MissingValuesInGrouping.TREAT_AS_NA.value:
        # Standardize missing-like values to a string label
        df[grouping_column] = df[grouping_column].fillna("N/A")
    else:
        raise ValueError(f"Unknown MissingValuesInGrouping option: {cfg.grouping_missing}")

    return df
