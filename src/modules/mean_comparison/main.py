#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

from src.common.decorators import log_function
from src.data.data import Data
from src.modules.mean_comparison.anova import recalculate_mean_comparison_anova
from src.modules.mean_comparison.preprocessing import prepare_df_for_mean_comparison
from src.modules.mean_comparison.result import MeanComparisonResult
from src.modules.mean_comparison.t_test import recalculate_mean_comparison_t_test


@log_function
def recalculate_mean_comparison_study(data: Data, result: MeanComparisonResult) -> MeanComparisonResult:
    cfg = result.config
    result.update_header()
    result.result_elements = []

    # Apply filters and grouping-missing policy
    df = prepare_df_for_mean_comparison(data=data, cfg=cfg)

    n_unique_values_in_grouping_column = len(df[cfg.grouping_column].unique())
    if n_unique_values_in_grouping_column < 2:
        msg = f"Not enough unique values in grouping column: {df[cfg.grouping_column].unique()}"
        result.set_placeholder(msg)
        logging.debug(msg)
        return result
    if n_unique_values_in_grouping_column == 2:
        n_rows_per_group = df.groupby(cfg.grouping_column).size()
        if n_rows_per_group.min() < 3:
            msg = f"Insufficient population in some groups: {n_rows_per_group.to_dict()}"
            result.set_placeholder(msg)
            logging.debug(msg)
            return result
        return recalculate_mean_comparison_t_test(data, result)

    n_rows_per_group = df.groupby(cfg.grouping_column).size()
    if n_rows_per_group.min() < 3:
        msg = f"Insufficient population in some groups: {n_rows_per_group.to_dict()}"
        result.set_placeholder(msg)
        logging.debug(msg)
        return result
    return recalculate_mean_comparison_anova(data, result)
