#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

import logging
from typing import Dict, Union

import pandas as pd

from src.common.decorators import log_function
from src.modules.mean_comparison.anova import recalculate_mean_comparison_anova
from src.modules.mean_comparison.result import MeanComparisonResult, MeanComparisonStudyConfig
from src.modules.mean_comparison.t_test import recalculate_mean_comparison_t_test


@log_function
def recalculate_mean_comparison_study(
    df: pd.DataFrame, result: MeanComparisonResult, ordinal_orders: Dict[str, Dict[Union[int, float, str], int]]
) -> MeanComparisonResult:
    config: MeanComparisonStudyConfig = result.config

    if len(config.selected_columns) < 1 or config.grouping_column is None:
        msg = "Please select one Grouping Column and at least one Variable"
        result.set_placeholder(msg)
        logging.debug(msg)
        return result

    if len(config.filters) > 0:
        for filter_settings in config.filters:
            query = filter_settings.get_query()
            logging.debug(f"Applying Filter: {query}")
            df = df.query(query)
    else:
        logging.debug("No filter applied")

    df = df[config.selected_columns + [config.grouping_column]]
    n_unique_values_in_grouping_column = len(df[config.grouping_column].unique())
    if n_unique_values_in_grouping_column < 2:
        msg = f"Not enough unique values in grouping column: {df[config.grouping_column].unique()}"
        result.set_placeholder(msg)
        logging.debug(msg)
        return result
    elif n_unique_values_in_grouping_column == 2:
        n_rows_per_group = df.groupby(config.grouping_column).size()
        if n_rows_per_group.min() < 3:
            msg = f"Insufficient population in some groups: {n_rows_per_group.to_dict()}"
            result.set_placeholder(msg)
            logging.debug(msg)
            return result
        return recalculate_mean_comparison_t_test(df, config, result, ordinal_orders)
    else:
        n_rows_per_group = df.groupby(config.grouping_column).size()
        if n_rows_per_group.min() < 3:
            msg = f"Insufficient population in some groups: {n_rows_per_group.to_dict()}"
            result.set_placeholder(msg)
            logging.debug(msg)
            return result
        return recalculate_mean_comparison_anova(df, config, result, ordinal_orders)
