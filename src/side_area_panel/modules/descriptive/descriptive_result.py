#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import attrs

from src.side_area_panel.modules.common.result.registry import BaseResult
from src.side_area_panel.modules.descriptive.constant import DESCRIPTION


@attrs.define
class DescriptiveStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)


class DescriptiveResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: DescriptiveStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Descriptive Statistics"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = DescriptiveStudyConfig
        self.config: DescriptiveStudyConfig = config

        self.needs_update: bool = False
        self.description = DESCRIPTION
        self.set_placeholder()
