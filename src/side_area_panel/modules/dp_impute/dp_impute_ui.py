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
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.dp_impute.dp_impute_result import IMPUTE_METHODS


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Columns:",
                column_type=ColumnType.NOMINAL,
                reasonable_number_of_columns=8,
                minimum_columns=1,
            ),
        ],
    )
    spacer = IISPWACSpacer()
    method = IISPWACComboBox(label_text="Method:", items=IMPUTE_METHODS)
    constant_value = IISPWACLongTextEdit(
        label_text="Constant value:",
        enabled_when=lambda kwargs: kwargs.get("method") == "Constant value",
    )


class Impute(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Impute Missing")
