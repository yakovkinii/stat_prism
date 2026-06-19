#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

from src.common.decorators import log_function
from src.common.translations import t
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

# Smallest per-group sample size the tests can run on.
_MIN_GROUP_SIZE = 3


def _fail(result: MeanComparisonResult, message: str) -> MeanComparisonResult:
    """Show a validation message to the user and log it, then stop."""
    logging.warning("T-test/ANOVA: %s", message)
    result.set_error(message)
    return result


@log_function
def recalculate_mean_comparison_study(elements: Elements, result: MeanComparisonResult, update) -> MeanComparisonResult:
    """Validate the inputs, then route to the t-test family (two groups) or the
    ANOVA family (three or more groups). Unexpected exceptions are handled centrally
    by the panel's recalculate()."""
    cfg = result.config
    result.result_elements = []

    grouping_columns = cfg.column_selector[1]
    if len(grouping_columns) != 1:
        return _fail(result, t("ttest.error.one_grouping"))
    grouping_column = grouping_columns[0]

    if cfg.assumption_checks == AssumptionChecksInGrouping.NEVER.value and (
        cfg.method == MeanComparisonMethod.AUTO.value
    ):
        return _fail(result, t("ttest.error.auto_no_assumptions"))

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    df = prepare_df_for_mean_comparison(data=data, cfg=cfg)

    groups = list(df[grouping_column].dropna().unique())
    if len(groups) < 2:
        return _fail(result, t("ttest.error.not_enough_groups", groups=", ".join(map(str, groups))))

    group_sizes = df.groupby(grouping_column).size()
    if group_sizes.min() < _MIN_GROUP_SIZE:
        return _fail(result, t("ttest.error.insufficient_population", groups=str(group_sizes.to_dict())))

    selected_columns = cfg.column_selector[0]
    result.title_context = ", ".join(col[:16] for col in selected_columns)
    if grouping_column:
        result.title_context += "\n" + str(grouping_column)[:16]

    update(5)
    if len(groups) == 2:
        result = recalculate_mean_comparison_t_test(data, result, update)
    else:
        result = recalculate_mean_comparison_anova(data, result, update)
    update(100)
    return result
