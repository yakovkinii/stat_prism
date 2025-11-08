#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.dp_process_column.dp_process_column_result import (
    ProcessColumnResult,
)
from src.side_area_panel.modules.dp_process_column.dp_process_column_ui import Elements


@log_function
def dp_process_column_main(elements: Elements, result: ProcessColumnResult):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )

    if cfg.column_selector[0] in [None, []]:
        elements.column_selector.set_alert(0)
        result.data = data.copy()
        return result

    result.data = data.copy()
    return result
