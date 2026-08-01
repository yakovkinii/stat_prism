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


import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class CFAStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    n_factors = attrs.field(default=None)
    estimator = attrs.field(default=None)
    allow_factor_correlation = attrs.field(default=None)
    second_order = attrs.field(default=None)
    modification_hints = attrs.field(default=None)
    cross_loadings = attrs.field(default=None)  # applied cross-loadings: [[item, factor_index], ...]
    verbal_indicators = attrs.field(default=None)
    interpretation = attrs.field(default=None)
    number_columns = attrs.field(default=None)
    plots = attrs.field(default=None)


class CFAResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: CFAStudyConfig):
        super().__init__(unique_id)
        self.title = "Confirmatory Factor Analysis"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = CFAStudyConfig
        self.config: CFAStudyConfig = config
        self.needs_update: bool = False
        # Residual-based cross-loading suggestions from the last fit: [(item, factor_index, score)].
        # The "Apply cross-loadings" element reads this to offer them for application.
        self.suggested_cross_loadings = []
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localized; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("cfa.description")
            + HTML.hr()
            + HTML.div(t("confirmatory_factor_analysis.fine_print"), font_size=Style.FontSize.smaller)
        )
