#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

from typing import List

from src.common.constant import ColumnType
from src.common.elements.filter.filter import FilterSettings
from src.common.result.classes.base_result import BaseResult
from src.modules.mean_comparison.constant import DESCRIPTION, MeanComparisonMethod


class MeanComparisonStudyConfig:
    def __init__(
        self,
        method: MeanComparisonMethod = None,
        selected_columns: List[str] = None,
        selected_columns_types: List[ColumnType] = None,
        grouping_column: str = None,
        filters: List[FilterSettings] = None,
    ):
        self.method = method if method is not None else MeanComparisonMethod.AUTO
        self.selected_columns = selected_columns if selected_columns is not None else []
        self.selected_columns_types = selected_columns_types if selected_columns_types is not None else []
        self.grouping_column = grouping_column
        self.generate_plots = True
        self.filters: List[FilterSettings] = filters if filters is not None else []


class MeanComparisonResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: MeanComparisonStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Mean Comparison"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config: MeanComparisonStudyConfig = config

        self.needs_update: bool = False
        self.description = DESCRIPTION
        self.set_placeholder()

    def rename_column(self, old_name, new_name):
        self.config.selected_columns = [new_name if col == old_name else col for col in self.config.selected_columns]
        if self.config.grouping_column == old_name:
            self.config.grouping_column = new_name
        self.needs_update = True

    def update_header(self):
        self.init_header("Mean Comparison")
        self.add_header_info("Method: " + self.config.method.value)
        self.add_header_info("Variables: " + ", ".join(self.config.selected_columns))
        self.add_header_info("Grouping Column: " + self.config.grouping_column)
        self.add_header_info(
            "Filters: " + (", ".join([str(f) for f in self.config.filters]) if self.config.filters else "None")
        )
