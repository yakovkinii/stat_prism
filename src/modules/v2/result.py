#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#
import logging
from typing import List

from src.common.elements.filter.filter import FilterSettings
from src.common.result.classes.base_result import BaseResult


class V2StudyConfig:
    def __init__(
        self,
        selected_columns: List[str] = None,
        filters: List[FilterSettings] = None,
    ):
        self.selected_columns = selected_columns if selected_columns is not None else []
        self.filters: List[FilterSettings] = filters if filters is not None else []


class V2Result(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: V2StudyConfig):
        super().__init__(unique_id, v2=False)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "V2"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config: V2StudyConfig = config

        self.needs_update: bool = False
        self.description = "V2 description"
        self.set_placeholder()

    def rename_column(self, old_name, new_name):
        self.config.selected_columns = [new_name if col == old_name else col for col in self.config.selected_columns]
        self.needs_update = True

    def update_header(self):
        try:
            self.init_header("V2")
            self.add_header_info("Variables: " + ", ".join(self.config.selected_columns))
            self.add_header_info(
                "Filters: " + (", ".join([str(f) for f in self.config.filters]) if self.config.filters else "None")
            )
        except Exception as e:
            logging.error(str(e))
            self.add_header_info("Error: " + str(e))
