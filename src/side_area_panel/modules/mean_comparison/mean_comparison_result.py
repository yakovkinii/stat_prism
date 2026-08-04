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
class MeanComparisonStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    method = attrs.field(default=None)
    grouping_missing = attrs.field(default=None)
    assumption_checks = attrs.field(default=None)
    effect_size = attrs.field(default=None)
    verbal_indicators = attrs.field(default=None)
    interpretation = attrs.field(default=None)
    confidence_intervals = attrs.field(default=None)
    number_columns = attrs.field(default=None)
    plots = attrs.field(default=None)
    bin_width = attrs.field(default=None)
    bin_reference = attrs.field(default=None)

    def __getstate__(self):
        return {field.name: getattr(self, field.name) for field in attrs.fields(type(self))}

    def __setstate__(self, state):
        # Support save files from v1.2.4 and earlier, which were pickled before bin_width /
        # bin_reference were added. attrs' generated __setstate__ leaves any field missing
        # from the old pickle unset, so a later attrs.asdict() raises AttributeError. Seed
        # every field with its default first, then apply whatever the pickle stored.
        fields = attrs.fields(type(self))
        if isinstance(state, tuple):
            state = dict(zip([field.name for field in fields], state))
        for field in fields:
            object.__setattr__(self, field.name, state.get(field.name, field.default))


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
        self.description = (
            t("ttest.description")
            + HTML.hr()
            + HTML.div(t("mean_comparison.fine_print"), font_size=Style.FontSize.smaller)
        )
