#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_result import CalculateScaleResult
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_ui import Elements


@log_function
def dp_calculate_scale_main(elements: Elements, result: CalculateScaleResult):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    result.data = data.copy()

    if cfg.column_selector[0] in [None, []]:
        elements.column_selector.set_alert(0)
        return result

    column_names = cfg.column_selector[0]
    # column = data[original_column_name].copy()
    scale_name = cfg.name
    if scale_name is None or scale_name.strip() == "":
        elements.name.set_alert()
        return result


    columns = data.get_dataframe(

    )
    data.add_column_after(original_column_name, column)

    if cfg.scale == "Stanine":
        min_val = column.data_series.min()
        max_val = column.data_series.max()
        def stanine_transform(x):
            if x <= min_val:
                return 1
            elif x >= max_val:
                return 9
            else:
                return int(((x - min_val) / (max_val - min_val)) * 8) + 1
        column.data_series = column.data_series.apply(stanine_transform)
    elif cfg.scale == "None":
        pass
    else:
        raise ValueError(f"Unknown scale option: {cfg.scale}")

    result.data = data.copy()
    return result
