#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class ContingencyStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    continuity_correction = attrs.field(default=None)
    effect_size = attrs.field(default=None)
    verbal_indicators = attrs.field(default=None)
    plots = attrs.field(default=None)


class ContingencyResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ContingencyStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Contingency Table"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = ContingencyStudyConfig
        self.config: ContingencyStudyConfig = config

        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("contingency.description")
            + HTML.hr()
            + HTML.div(t("contingency.fine_print"), font_size=Style.FontSize.smaller)
        )
