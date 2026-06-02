#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import pandas as pd

from src.common.decorators import log_function
from src.data.data import DataColumn
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import unique_name
from src.side_area_panel.modules.dp_row_id.dp_row_id_result import RowIdResult
from src.side_area_panel.modules.dp_row_id.dp_row_id_ui import Elements


@log_function
def dp_row_id_main(elements: Elements, result: RowIdResult):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    new_data = data.copy()

    if new_data.n_columns() == 0:
        result.data = new_data
        return result

    index = new_data.columns[0].data_series.index
    name = unique_name("ID", set(new_data.column_names()))
    id_series = pd.Series(range(1, len(index) + 1), index=index, name=name)
    new_data.add_column_first(DataColumn.initialize_from_series(id_series))

    result.data = new_data
    return result
