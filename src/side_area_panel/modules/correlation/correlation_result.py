#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum

import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


class CorrelationType(Enum):
    PEARSON = 0
    SPEARMAN = 1
    KENDALL = 2
    PHI = 3
    TETRACHORIC = 4
    POLYCHORIC = 5
    KENDALL_C = 6


CORRELATION_TYPE_MAP = {
    "Pearson": CorrelationType.PEARSON,
    "Spearman": CorrelationType.SPEARMAN,
    "Kendall": CorrelationType.KENDALL,
    "Kendall tau c": CorrelationType.KENDALL_C,
    "Phi": CorrelationType.PHI,
    "Tetrachoric": CorrelationType.TETRACHORIC,
    "Polychoric": CorrelationType.POLYCHORIC,
}


@attrs.define
class CorrelationStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    correlation_type = attrs.field(default=None)
    compact = attrs.field(default=None)
    generate_heatmap = attrs.field(default=None)
    generate_plots = attrs.field(default=None)
    report_only_significant = attrs.field(default=None)


class CorrelationResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: CorrelationStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Correlation"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = CorrelationStudyConfig
        self.config: CorrelationStudyConfig = config

        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("correlation.description")
            + HTML.hr()
            + HTML.div(t("correlation.fine_print"), font_size=Style.FontSize.smaller)
        )
