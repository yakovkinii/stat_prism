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


import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult

_METHODOLOGY = (
    "<b>Filter</b><br>"
    "Keeps only the rows that match a condition on one column. For a numeric column, keep rows "
    "where the value satisfies a comparison (&lt;, &le;, =, &ge;, &gt;, &ne;) against a value, or "
    "use <i>is empty</i> / <i>is not empty</i> to filter on missing cells; for a categorical "
    "column, keep only the ticked category values (a <i>(empty)</i> option appears when the column "
    'has blank cells). Empty matches both NaN and "". Rows that don\'t match are removed '
    "downstream. Previewing the data shows removed rows in red. Toggle the step off (card button) "
    "to keep all rows."
)


@attrs.define
class FilterDataStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    column_filter = attrs.field(default=None)
    enabled = attrs.field(default=True)


class FilterDataResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: FilterDataStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Filter"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = FilterDataStudyConfig
        self.config: FilterDataStudyConfig = config
        self.needs_update: bool = False
        # Tells the result card to show the large enable/disable toggle.
        self.toggleable: bool = True
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])
        # For the data-preview popup: the unfiltered data plus the row positions that were
        # removed, so the popup can show every row with the removed ones in red.
        self.full_data = Data([])
        self.removed_positions = []

    def update_description(self):
        cfg = self.config
        selected = cfg.column_selector[0] if cfg.column_selector else []
        column = selected[0] if selected else "(none)"
        parts = [f"Column: {column}"]

        spec = cfg.column_filter
        if spec and spec.get("column") == column:
            if spec.get("mode") == "numeric":
                value = spec.get("value")
                if value not in (None, ""):
                    parts.append(f"Keep where {column} {spec.get('operation')} {value}")
            elif spec.get("mode") == "categorical":
                kept = spec.get("kept_values")
                if kept is not None:
                    parts.append("Keep values: " + (", ".join(str(v) for v in kept) if kept else "(none)"))

        parts.append("Status: enabled" if cfg.enabled else "Status: disabled")
        self.description = "<br>".join(parts)
