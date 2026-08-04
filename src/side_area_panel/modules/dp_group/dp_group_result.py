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

# Where a value exactly on a split point lands. Default sends it to the higher group, so the
# bins are left-closed [a, b) -- consistent with the usual histogram convention.
SPLIT_SIDES = ["Higher group", "Lower group"]

_METHODOLOGY = (
    "<b>Group values</b><br>"
    "Bins a numeric column into ordered groups using the split points you provide (e.g. split "
    "points 3, 6 give three bins). <b>Split point goes to</b> controls which side a value that "
    "is exactly on a split point lands on: <i>Higher group</i> (default) makes the bins "
    "left-closed [a, b) &mdash; e.g. &lt;3, 3&ndash;6, &ge;6; <i>Lower group</i> makes them "
    "right-closed (a, b] &mdash; e.g. &le;3, 3&ndash;6, &gt;6. Each bin can be given a label; "
    "the result is added as a new column, leaving the original untouched."
)


@attrs.define
class GroupValuesStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    thresholds = attrs.field(default=None)
    names = attrs.field(default=None)
    new_name = attrs.field(default=None)
    split_side = attrs.field(default=None)


class GroupValuesResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: GroupValuesStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Group Values"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = GroupValuesStudyConfig
        self.config: GroupValuesStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        selected = cfg.column_selector[0] if cfg.column_selector else []
        column = selected[0] if selected else "(none)"
        parts = [f"Column: {column}"]
        if cfg.thresholds:
            parts.append(f"Split points: {cfg.thresholds}")
            parts.append(f"Split point goes to: {cfg.split_side or SPLIT_SIDES[0]}")
        self.description = "<br>".join(parts)
