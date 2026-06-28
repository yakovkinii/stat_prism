#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.outlier_logic import detect_nd_outliers
from src.side_area_panel.modules.common.removal import clear_removal, finalize_removal
from src.side_area_panel.modules.dp_2d_outliers.dp_2d_outliers_result import TwoDOutliersResult
from src.side_area_panel.modules.dp_2d_outliers.dp_2d_outliers_ui import Elements


@log_function
def dp_2d_outliers_main(elements: Elements, result: TwoDOutliersResult, update):
    """Flag multivariate (N-dimensional) outliers across the selected columns using the
    Mahalanobis distance of each row from the joint centre, with a chi-square cutoff
    (df = number of columns) at 95% confidence. This accounts for the correlations between
    the columns, unlike per-column thresholds. Needs at least two columns."""
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )

    if not cfg.enabled:
        return clear_removal(result, data)  # disabled -> no-op, stays in chain

    selected = cfg.column_selector[0] if cfg.column_selector else None
    if not selected or len(selected) < 2:
        # ND outliers are undefined for a single column -> flag the input.
        elements.column_selector.set_alert(0)
        return clear_removal(result, data, "Select two or more columns.")

    candidates = detect_nd_outliers(data, selected)
    return finalize_removal(result, data, candidates, cfg.remove_list)
