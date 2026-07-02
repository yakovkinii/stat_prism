#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import attrs

from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult

_DESCRIPTION = (
    "Summarises a multi-select (&lsquo;checkbox&rsquo;) question whose options have been split "
    "into 0/1 indicator columns (see the <b>Split Multi-Select</b> step). Select all the "
    "indicator columns that came from one question; the table reports, per option, how many "
    "respondents chose it and the share of responses and of respondents."
)

_FINE_PRINT = (
    "<b>Methodology &amp; assumptions</b>"
    "<ul>"
    "<li><b>Selected</b> counts a respondent for an option when that option&rsquo;s indicator "
    "column is 1 (any non-zero value counts as selected).</li>"
    "<li><b>% of responses</b> = selections of this option / total selections across all options "
    "(these sum to 100%).</li>"
    "<li><b>% of cases</b> = selections of this option / number of respondents who chose at least "
    "one option. These sum to more than 100% because a respondent can choose several options.</li>"
    "<li><b>Cases</b> excludes respondents who selected nothing (all indicators 0 / missing).</li>"
    "</ul>"
)


@attrs.define
class MultipleResponseStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    show_chart = attrs.field(default=None)
    interpretation = attrs.field(default=None)


class MultipleResponseResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: MultipleResponseStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Multiple Response"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = MultipleResponseStudyConfig
        self.config: MultipleResponseStudyConfig = config
        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        self.description = _DESCRIPTION + HTML.hr() + HTML.div(_FINE_PRINT, font_size=Style.FontSize.smaller)
