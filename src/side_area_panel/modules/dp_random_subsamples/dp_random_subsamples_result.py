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
    "<b>Random sub-samples</b><br>"
    "Adds a nominal column with randomly assigned sub-sample labels. Assignments can be "
    "specified as exact counts or as percentages. The last allocation is always the remaining "
    "group, so the generated column contains exactly one label per row. Percentages are converted "
    "to integer row counts by largest-remainder rounding. The fixed seed is 0, so assignments are "
    "reproducible."
)


@attrs.define
class RandomSubsamplesStudyConfig:
    data_source = attrs.field(default=None)
    new_name = attrs.field(default=None)
    assignment_mode = attrs.field(default=None)
    allocations = attrs.field(default=None)


class RandomSubsamplesResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: RandomSubsamplesStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Random Sub-samples"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = RandomSubsamplesStudyConfig
        self.config: RandomSubsamplesStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.methodology = _METHODOLOGY
        self.assignment_summary = ""
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        name = (cfg.new_name or "").strip() or "Subsample"
        mode = cfg.assignment_mode or "Counts"
        lines = [f"New column: {name}", f"Mode: {mode}"]
        if self.assignment_summary:
            lines.append(self.assignment_summary)
        self.description = "<br>".join(lines)
