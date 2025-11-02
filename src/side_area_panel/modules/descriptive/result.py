#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import List

from src.pyside_ext.elements.filter import FilterSettings
from src.side_area_panel.modules.common.result.registry import BaseResult
from src.side_area_panel.modules.descriptive.constant import DESCRIPTION


class DescriptiveStudyConfig:
    def __init__(
        self,
        selected_columns: List[str] = None,
        grouping_column: str = None,
        filters: List[FilterSettings] = None,
    ):
        self.selected_columns = selected_columns if selected_columns is not None else []
        self.grouping_column = grouping_column
        self.filters: List[FilterSettings] = filters if filters is not None else []


class DescriptiveResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: DescriptiveStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Descriptive Statistics"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config: DescriptiveStudyConfig = config

        self.needs_update: bool = False
        self.description = DESCRIPTION
        self.set_placeholder()

    def rename_column(self, old_name, new_name):
        self.config.selected_columns = [new_name if col == old_name else col for col in self.config.selected_columns]
        if self.config.grouping_column == old_name:
            self.config.grouping_column = new_name
        self.needs_update = True
