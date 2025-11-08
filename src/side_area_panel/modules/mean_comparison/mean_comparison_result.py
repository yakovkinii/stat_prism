#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

import attrs

from src.side_area_panel.modules.common.result.registry import BaseResult
from src.side_area_panel.modules.mean_comparison.constant import DESCRIPTION


@attrs.define
class MeanComparisonStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    method = attrs.field(default=None)
    grouping_missing = attrs.field(default=None)
    assumption_checks = attrs.field(default=None)
    effect_size = attrs.field(default=None)
    means = attrs.field(default=None)
    plots = attrs.field(default=None)


class MeanComparisonResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: MeanComparisonStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "T-test/ANOVA"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = MeanComparisonStudyConfig
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
        try:
            self.init_header("T-test/ANOVA")
            self.add_header_info("Method: " + self.config.method.value)
            self.add_header_info("Variables: " + ", ".join(self.config.selected_columns))
            self.add_header_info("Grouping Column: " + self.config.grouping_column)
            self.add_header_info(
                "Filters: " + (", ".join([str(f) for f in self.config.filters]) if self.config.filters else "None")
            )
        except Exception as e:
            logging.error(str(e))
            self.add_header_info("Error: " + str(e))

    def update_description(self):
        pass
