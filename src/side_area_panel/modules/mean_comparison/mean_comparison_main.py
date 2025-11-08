#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.mean_comparison.anova import (
    recalculate_mean_comparison_anova,
)
from src.side_area_panel.modules.mean_comparison.constant import (
    AssumptionChecksInGrouping,
    MeanComparisonMethod,
)
from src.side_area_panel.modules.mean_comparison.mean_comparison_result import (
    MeanComparisonResult,
)
from src.side_area_panel.modules.mean_comparison.mean_comparison_ui import Elements
from src.side_area_panel.modules.mean_comparison.preprocessing import (
    prepare_df_for_mean_comparison,
)
from src.side_area_panel.modules.mean_comparison.t_test import (
    recalculate_mean_comparison_t_test,
)


@log_function
def recalculate_mean_comparison_study(elements: Elements, result: MeanComparisonResult) -> MeanComparisonResult:
    cfg = result.config

    grouping_columns = cfg.column_selector[1]
    if len(grouping_columns) != 1:
        msg = "Please select exactly one grouping column."
        result.set_placeholder(msg)
        logging.debug(msg)
        return result
    grouping_column = grouping_columns[0]

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )

    result.update_header()
    result.result_elements = []

    # Apply filters and grouping-missing policy
    df = prepare_df_for_mean_comparison(data=data, cfg=cfg)

    n_unique_values_in_grouping_column = len(df[grouping_column].unique())
    if n_unique_values_in_grouping_column < 2:
        msg = f"Not enough unique values in grouping column: {df[grouping_column].unique()}"
        result.set_placeholder(msg)
        logging.debug(msg)
        return result

    if (cfg.assumption_checks == AssumptionChecksInGrouping.NEVER.value) and (
        cfg.method == MeanComparisonMethod.AUTO.value
    ):
        msg = f"Assumption checks are disabled and method is set to AUTO. Cannot determine appropriate test."
        result.set_placeholder(msg)
        logging.debug(msg)
        return result

    if n_unique_values_in_grouping_column == 2:
        n_rows_per_group = df.groupby(grouping_column).size()
        if n_rows_per_group.min() < 3:
            msg = f"Insufficient population in some groups: {n_rows_per_group.to_dict()}"
            result.set_placeholder(msg)
            logging.debug(msg)
            return result
        return recalculate_mean_comparison_t_test(data, result)

    n_rows_per_group = df.groupby(grouping_column).size()
    if n_rows_per_group.min() < 3:
        msg = f"Insufficient population in some groups: {n_rows_per_group.to_dict()}"
        result.set_placeholder(msg)
        logging.debug(msg)
        return result
    return recalculate_mean_comparison_anova(data, result)
