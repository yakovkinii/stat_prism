#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class ProcessColumnStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    rename = attrs.field(default=None)
    flip = attrs.field(default=None)
    scale = attrs.field(default=None)


class ProcessColumnResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ProcessColumnStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Process Column"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = ProcessColumnStudyConfig
        self.config: ProcessColumnStudyConfig = config
        self.needs_update: bool = False
        self.description = ...
        self.update_description()

        self.data = Data([])

    def update_description(self):
        self.description = str(attrs.asdict(self.config))
