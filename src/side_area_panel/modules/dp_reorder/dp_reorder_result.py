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

# Where the selected block is placed relative to the columns left untouched. The two "position of"
# options drop the block back where the first / last selected column used to sit (identical when the
# selected columns were already one contiguous run).
POS_FRONT = "Move to front"
POS_BACK = "Move to back"
POS_FIRST = "First selected"
POS_LAST = "Last selected"
POSITIONS = [POS_FRONT, POS_BACK, POS_FIRST, POS_LAST]

_METHODOLOGY = (
    "<b>Reorder columns</b><br>"
    "Rearranges the dataset's column order. The columns you select move together, in the order "
    "you arrange them, either to the front or the back; the columns left unselected keep their "
    "relative order. The ID column always stays first. Only the column order changes &mdash; the "
    "values are untouched."
)


@attrs.define
class ReorderColumnsStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    position = attrs.field(default=None)


class ReorderColumnsResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ReorderColumnsStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Reorder Columns"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = ReorderColumnsStudyConfig
        self.config: ReorderColumnsStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        selected = (cfg.column_selector[0] if cfg.column_selector else []) or []
        parts = [f"Place: {cfg.position or POSITIONS[0]}"]
        parts.append(f"Moved ({len(selected)}): " + (", ".join(selected) if selected else "none"))
        self.description = "<br>".join(parts)
