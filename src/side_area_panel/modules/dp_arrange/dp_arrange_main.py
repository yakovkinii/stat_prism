#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.


from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.data.data import Data
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.dp_arrange.dp_arrange_result import ArrangeColumnsResult
from src.side_area_panel.modules.dp_arrange.dp_arrange_ui import Elements


@log_function
def dp_arrange_main(elements: Elements, result: ArrangeColumnsResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    new_data = data.copy()
    result.error_message = ""

    order = cfg.order or []
    # The ID column is a fixed anchor and always stays leftmost.
    id_columns = [column for column in new_data.columns if column.column_type == ColumnType.ID]
    others = [column for column in new_data.columns if column.column_type != ColumnType.ID]
    by_name = {column.column_name: column for column in others}

    order_set = set(order)
    ordered = [by_name[name] for name in order if name in by_name]
    # Columns not in the saved order (e.g. added by a later edit) keep their relative order, at end.
    ordered += [column for column in others if column.column_name not in order_set]

    result.data = Data(id_columns + ordered)
    return result
