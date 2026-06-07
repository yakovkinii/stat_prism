#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import attrs

from src.common.translations import t
from src.side_area_panel.modules.common.result.registry import BaseResult


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
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # Resolved against the current language each time it is shown.
        self.description = t("ttest.description")
