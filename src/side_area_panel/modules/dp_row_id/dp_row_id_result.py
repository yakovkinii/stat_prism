#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class RowIdStudyConfig:
    data_source = attrs.field(default=None)


class RowIdResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: RowIdStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Row ID"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = RowIdStudyConfig
        self.config: RowIdStudyConfig = config
        self.needs_update: bool = False
        self.description = "Adds an ID column (the row number) as the first column."

        self.data = Data([])

    def update_description(self):
        pass
