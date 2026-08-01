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
    interpretation = attrs.field(default=None)
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
        # General guide is localized; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("reliability.description")
            + HTML.hr()
            + HTML.div(t("reliability.fine_print"), font_size=Style.FontSize.smaller)
        )
