#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.cleaning_logic import CHECKS, detect_response_quality
from src.side_area_panel.modules.common.removal import clear_removal, finalize_removal
from src.side_area_panel.modules.dp_response_quality.dp_response_quality_result import ResponseQualityResult
from src.side_area_panel.modules.dp_response_quality.dp_response_quality_ui import Elements


@log_function
def dp_response_quality_main(elements: Elements, result: ResponseQualityResult, update):
    """Flag low-quality respondents (duplicates, straightlining, missingness, low variability)
    and drop the ones still ticked in the Remove list, recording removed rows for the red
    preview."""
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
        return clear_removal(result, data, "Select at least one question.")

    check = cfg.check or CHECKS[0]
    threshold = cfg.threshold if cfg.threshold is not None else 50
    candidates = detect_response_quality(data, check, selected, threshold)
    return finalize_removal(result, data, candidates, cfg.remove_list)
