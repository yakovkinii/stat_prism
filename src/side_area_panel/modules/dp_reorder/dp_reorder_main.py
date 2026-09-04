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

#  DEPRECATED: superseded by Arrange Columns; kept in 1.2.8 for backward compatibility only (see
#  dp_reorder_result). Slated for removal in 1.3.0.

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.data.data import Data
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.dp_reorder.dp_reorder_result import (
    POS_BACK,
    POS_FIRST,
    POS_FRONT,
    ReorderColumnsResult,
)
from src.side_area_panel.modules.dp_reorder.dp_reorder_ui import Elements


@log_function
def dp_reorder_main(elements: Elements, result: ReorderColumnsResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    new_data = data.copy()
    result.data = new_data
    result.error_message = ""

    selected = (cfg.column_selector[0] if cfg.column_selector else None) or []

    # The ID column is a fixed anchor and always stays leftmost; only the other columns move.
    id_columns = [column for column in new_data.columns if column.column_type == ColumnType.ID]
    others = [column for column in new_data.columns if column.column_type != ColumnType.ID]
    by_name = {column.column_name: column for column in others}

    # Selected columns in the chosen order (dropping any that no longer exist); the rest keep
    # their original relative order.
    moved = [by_name[name] for name in selected if name in by_name]
    moved_names = {column.column_name for column in moved}
    rest = [column for column in others if column.column_name not in moved_names]

    position = cfg.position or POS_FRONT
    if not moved or position == POS_FRONT:
        ordered = moved + rest
    elif position == POS_BACK:
        ordered = rest + moved
    else:
        # Drop the block back where the first / last selected column used to sit: find that
        # reference column's original index, then insert the block after every kept column that
        # was originally before it.
        moved_positions = [i for i, column in enumerate(others) if column.column_name in moved_names]
        reference = min(moved_positions) if position == POS_FIRST else max(moved_positions)
        insert_at = sum(1 for i, column in enumerate(others) if i < reference and column.column_name not in moved_names)
        ordered = rest[:insert_at] + moved + rest[insert_at:]

    result.data = Data(id_columns + ordered)
    return result
