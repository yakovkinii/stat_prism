#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.

# VALIDATED


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
    confidence_intervals = attrs.field(default=None)
    number_columns = attrs.field(default=None)
    interpretation = attrs.field(default=None)


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
        # General guide is localized; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("correlation.description")
            + HTML.hr()
            + HTML.div(t("correlation.fine_print"), font_size=Style.FontSize.smaller)
        )
