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


from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.dp_filter.dp_filter_result import FilterDataResult
from src.side_area_panel.modules.dp_filter.dp_filter_ui import Elements
from src.side_area_panel.modules.dp_filter.filter_logic import (
    ALERT_COLUMN,
    ALERT_VALUE,
    apply_mask,
    compute_keep_mask,
    removed_positions,
)


def _set_no_filter(result, data):
    """Pass-through: keep every row, and record an empty removed set for the popup."""
    result.data = data.copy()
    result.full_data = data.copy()
    result.removed_positions = []
    return result


@log_function
def dp_filter_main(elements: Elements, result: FilterDataResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    result.error_message = ""

    # Disabled filter is a no-op but still occupies its slot in the data chain.
    if not cfg.enabled:
        return _set_no_filter(result, data)

    mask, error, alert = compute_keep_mask(data, cfg)
    if alert == ALERT_COLUMN:
        elements.column_selector.set_alert(0)
    elif alert == ALERT_VALUE:
        elements.column_filter.set_alert()
    if error:
        result.error_message = error
    if mask is None:
        return _set_no_filter(result, data)

    # Record the removed row positions (relative to the unfiltered row order) for the popup.
    result.full_data = data.copy()
    result.removed_positions = removed_positions(mask)
    result.data = apply_mask(data, mask)
    return result
