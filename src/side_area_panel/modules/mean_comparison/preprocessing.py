#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from __future__ import annotations

import pandas as pd

from src.data.data import Data
from src.side_area_panel.modules.mean_comparison.constant import MissingValuesInGrouping
from src.side_area_panel.modules.mean_comparison.result import MeanComparisonStudyConfig


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
    df = data.get_dataframe(
        filters=cfg.filters,
        columns=cfg.selected_columns + [cfg.grouping_column],
        map_ordinal=map_ordinal,
    ).copy()

    df.loc[
        df[cfg.grouping_column].isin(
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
        cfg.grouping_column,
    ] = pd.NA

    if cfg.grouping_missing == MissingValuesInGrouping.SKIP:
        df = df[df[cfg.grouping_column].notna()].copy()
    elif cfg.grouping_missing == MissingValuesInGrouping.TREAT_AS_NA:
        # Standardize missing-like values to a string label
        df[cfg.grouping_column] = df[cfg.grouping_column].fillna("N/A")
    else:
        raise ValueError(f"Unknown MissingValuesInGrouping option: {cfg.grouping_missing}")

    return df
