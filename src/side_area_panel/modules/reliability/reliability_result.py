#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class ReliabilityStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    correlation_type = attrs.field(default=None)
    scale_name = attrs.field(default=None)
    mcdonald_omega = attrs.field(default=None)
    item_deleted_table = attrs.field(default=None)
    verbal_indicators = attrs.field(default=None)
    number_columns = attrs.field(default=None)


class ReliabilityResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ReliabilityStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Reliability"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = ReliabilityStudyConfig
        self.config: ReliabilityStudyConfig = config

        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("reliability.description")
            + HTML.hr()
            + HTML.div(t("reliability.fine_print"), font_size=Style.FontSize.smaller)
        )
