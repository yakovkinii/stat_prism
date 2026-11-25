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

from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult

# Dropdown order = default first.
AGGREGATORS = ["Mean", "Sum", "Median"]

_DESCRIPTION = (
    "Draws a <b>rose plot</b> (a circular bar chart): one bar per selected column, its length the "
    "chosen aggregate of that column across respondents. It is a compact way to compare many "
    "variables on one radial scale &ndash; for example the mean of each item in a profile."
)

_FINE_PRINT = (
    "<b>Methodology &amp; assumptions</b>"
    "<ul>"
    "<li>Each bar&rsquo;s length is the <b>aggregate</b> (mean / sum / median) of that column over "
    "all respondents; ordinal columns are read as their numeric face values and non-numeric cells "
    "are ignored.</li>"
    "<li><b>Scale min / max</b> set the radial axis limits. Left blank, they are chosen "
    "automatically from the data (minimum clamped to 0 when all values are non-negative).</li>"
    "<li>Each ray is identified by its colour (see the legend); its aggregate value is printed "
    "just outside the rim &mdash; rounded to a fixed number of decimal places (by default one "
    "more than the data carries), and moved further out with the value-label distance.</li>"
    "<li>With many columns, <b>group shading</b> can shade alternating blocks of rays (and the "
    "matching legend rows) so they are easier to count.</li>"
    "</ul>"
)


@attrs.define
class RosePlotStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    aggregator = attrs.field(default=None)
    scale_min = attrs.field(default=None)
    scale_max = attrs.field(default=None)


class RosePlotResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: RosePlotStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Rose Plot"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = RosePlotStudyConfig
        self.config: RosePlotStudyConfig = config
        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        self.description = _DESCRIPTION + HTML.hr() + HTML.div(_FINE_PRINT, font_size=Style.FontSize.smaller)
