#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.outlier_logic import detect_univariate_outliers
from src.side_area_panel.modules.common.removal import clear_removal, finalize_removal
from src.side_area_panel.modules.dp_outliers.dp_outliers_result import OutliersResult
from src.side_area_panel.modules.dp_outliers.dp_outliers_ui import Elements


@log_function
def dp_outliers_main(elements: Elements, result: OutliersResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )

    if not cfg.enabled:
        return clear_removal(result, data)  # disabled -> no-op, stays in chain

    selected = cfg.column_selector[0] if cfg.column_selector else None
    if not selected:
        elements.column_selector.set_alert(0)
        return clear_removal(result, data, "Select at least one column.")

    candidates = detect_univariate_outliers(data, selected, cfg.method or "IQR")
    return finalize_removal(result, data, candidates, cfg.remove_list)
