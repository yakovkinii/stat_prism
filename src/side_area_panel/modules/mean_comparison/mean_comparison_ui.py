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


from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.prose import PROSE_LABEL, PROSE_LEVELS
from src.side_area_panel.modules.mean_comparison.constant import (
    AssumptionChecksInGrouping,
    MeanComparisonMethod,
    MissingValuesInGrouping,
)


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Variable(s):",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=8,
                minimum_columns=1,
            ),
            Field(
                name="Grouping Column:",
                column_type=ColumnType.NOMINAL,
                reasonable_number_of_columns=1,
                allow_only_single_column=True,
                minimum_columns=1,
            ),
        ],
    )
    spacer1 = IISPWACSpacer()
    method = IISPWACComboBox(
        label_text="Method:",
        items=MeanComparisonMethod.get_values(),
    )
    grouping_missing = IISPWACComboBox(
        label_text="Missing in grouping:",
        items=MissingValuesInGrouping.get_values(),
    )
    assumption_checks = IISPWACComboBox(
        label_text="Check assumptions:",
        items=AssumptionChecksInGrouping.get_values(),
    )
    effect_size = IISPWACCheckBox(
        label_text="Effect size/Post-hoc",
        default_state=False,
    )
    verbal_indicators = IISPWACCheckBox(
        label_text="Verbal indicators in tables",
        default_state=False,
    )
    interpretation = IISPWACComboBox(label_text=PROSE_LABEL, items=PROSE_LEVELS)
    confidence_intervals = IISPWACCheckBox(
        label_text="95% CI for Cohen's d",
        default_state=False,
    )
    number_columns = IISPWACCheckBox(
        label_text="Number variables in tables",
        default_state=False,
    )
    plots = IISPWACCheckBox(
        label_text="Plots",
        default_state=False,
    )
    bin_width = IISPWACLongTextEdit(
        label_text="Bin width (blank: auto):",
        visible_when=lambda kwargs: bool(kwargs.get("plots")),
    )
    bin_reference = IISPWACLongTextEdit(
        label_text="Bin reference (blank: auto):",
        visible_when=lambda kwargs: bool(kwargs.get("plots")),
    )


class MeanComparison(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("T-test/ANOVA")
