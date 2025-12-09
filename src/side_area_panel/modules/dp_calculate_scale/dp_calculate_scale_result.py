#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.common.decorators import log_method_noarg
from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class CalculateScaleStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    name = attrs.field(default=None)
    scale = attrs.field(default=None)

class CalculateScaleResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: CalculateScaleStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Calculate Scale"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = CalculateScaleStudyConfig
        self.config: CalculateScaleStudyConfig = config
        self.needs_update: bool = False
        self.description = ...
        self.update_description()

        self.data = Data([])

    def update_description(self):
        self.description = str(attrs.asdict(self.config))
