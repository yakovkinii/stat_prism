#  Copyright (c) 2023 StatPrism Team. All rights reserved.
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
