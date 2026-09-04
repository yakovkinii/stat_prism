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
    "<b>Arrange columns</b><br>"
    "Sets the dataset's column order by dragging every column into place in one list &mdash; no "
    "column selector. The ID column always stays first, and any columns added by a later step "
    "appear at the end until you move them. Only the order changes; the values are untouched."
)


@attrs.define
class ArrangeColumnsStudyConfig:
    data_source = attrs.field(default=None)
    order = attrs.field(default=None)


class ArrangeColumnsResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ArrangeColumnsStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Arrange Columns"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = ArrangeColumnsStudyConfig
        self.config: ArrangeColumnsStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])

    def update_description(self):
        order = self.config.order or []
        self.description = f"Columns ordered ({len(order)}): " + (", ".join(order) if order else "none")
