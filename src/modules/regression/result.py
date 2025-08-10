#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import List

from src.modules.common.result.registry import BaseResult
from src.modules.regression.constant import DESCRIPTION
from src.pyside_ext.elements.filter import FilterSettings


class RegressionStudyConfig:
    def __init__(
        self,
        dependent_column: str = None,
        independent_columns: List[str] = None,
        moderator_column: str = None,
        mediator_column: str = None,
        filters: List[FilterSettings] = None,
    ):
        self.dependent_column: str = dependent_column
        self.independent_columns: List[str] = independent_columns if independent_columns is not None else []
        self.moderator_column: str = moderator_column
        self.mediator_column: str = mediator_column
        self.filters: List[FilterSettings] = filters if filters is not None else []


class RegressionResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: RegressionStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Regression"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config: RegressionStudyConfig = config

        self.needs_update: bool = False
        self.description = DESCRIPTION
        self.set_placeholder()

    def rename_column(self, old_name, new_name):
        if self.config.dependent_column == old_name:
            self.config.dependent_column = new_name
        if self.config.moderator_column == old_name:
            self.config.moderator_column = new_name
        if self.config.mediator_column == old_name:
            self.config.mediator_column = new_name
        if old_name in self.config.independent_columns:
            self.config.independent_columns[self.config.independent_columns.index(old_name)] = new_name
        self.needs_update = True
