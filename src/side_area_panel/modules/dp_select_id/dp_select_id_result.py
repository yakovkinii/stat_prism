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
    "<b>Select ID column</b><br>"
    "Promotes the chosen column to be the data set's identifier: it is moved to the first "
    "position and renamed to &lsquo;ID&rsquo;, and the previous ID column is removed. The "
    "chosen column must have no missing values and only unique values; otherwise the column "
    "selector is highlighted and the data is left unchanged."
)


@attrs.define
class SelectIDStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)


class SelectIDResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: SelectIDStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Select ID Column"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = SelectIDStudyConfig
        self.config: SelectIDStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        selected = cfg.column_selector[0] if cfg.column_selector else []
        column = selected[0] if selected else "(none)"
        self.description = f"Identifier column: {column}"
