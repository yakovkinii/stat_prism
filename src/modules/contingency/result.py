#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import List

from src.common.elements.filter.filter import FilterSettings
from src.common.result.base_result import BaseResult
from src.modules.contingency.constant import DESCRIPTION


class ContingencyStudyConfig:
    def __init__(
        self,
        selected_column1: str = None,
        selected_column2: str = None,
        filters: List[FilterSettings] = None,
    ):
        self.selected_column1 = selected_column1
        self.selected_column2 = selected_column2
        self.filters: List[FilterSettings] = filters if filters is not None else []


class ContingencyResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ContingencyStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Contingency Table"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config: ContingencyStudyConfig = config

        self.needs_update: bool = False
        self.description = DESCRIPTION
        self.set_placeholder()

    def rename_column(self, old_name, new_name):
        if self.config.selected_column1 == old_name:
            self.config.selected_column1 = new_name
        if self.config.selected_column2 == old_name:
            self.config.selected_column2 = new_name
        self.needs_update = True
