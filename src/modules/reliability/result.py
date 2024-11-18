#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

from typing import List

from src.common.constant import ColumnType
from src.common.elements.filter.filter import FilterSettings
from src.common.result.classes.base_result import BaseResult
from src.modules.correlation.result import CorrelationType
from src.modules.reliability.constant import DESCRIPTION


class ReliabilityStudyConfig:
    def __init__(
        self,
        scale_column: str = None,
        selected_columns: List[str] = None,
        selected_columns_types: List[ColumnType] = None,
        correlation_type: CorrelationType = CorrelationType.PEARSON,
        filters: List[FilterSettings] = None,
    ):
        self.scale_column = scale_column
        self.selected_columns = selected_columns if selected_columns is not None else []
        self.selected_columns_types = selected_columns_types if selected_columns_types is not None else []
        self.generate_plots = True
        self.correlation_type = correlation_type
        self.filters: List[FilterSettings] = filters if filters is not None else []


class ReliabilityResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ReliabilityStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Reliability"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config: ReliabilityStudyConfig = config

        self.needs_update: bool = False
        self.description = DESCRIPTION
        self.set_placeholder()

    def rename_column(self, old_name, new_name):
        if self.config.scale_column == old_name:
            self.config.scale_column = new_name
        self.config.selected_columns = [new_name if col == old_name else col for col in self.config.selected_columns]
        self.needs_update = True
