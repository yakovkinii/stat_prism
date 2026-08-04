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
from src.side_area_panel.iispwac.iispwac_remove_list import IISPWACRemoveList
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.outlier_logic import detect_grouped_outliers


def _detect(data, params):
    selector = params.get("column_selector") or []
    columns = (selector[0] if len(selector) > 0 else []) or []
    grouping = (selector[1] if len(selector) > 1 else []) or []
    grouping_column = grouping[0] if grouping else None
    return detect_grouped_outliers(data, columns, grouping_column, params.get("method") or "IQR")


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()

    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Columns:",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=8,
                allow_only_single_column=False,
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

    method = IISPWACComboBox(label_text="Method:", items=["IQR", "Z-score"])
    remove_list = IISPWACRemoveList(detector=_detect)
    enabled = IISPWACCheckBox(label_text="Enable", default_state=True)


class GroupedOutliers(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Grouped Outliers")
        # The enable/disable control is the toggle on the result card.
        self.elements_.enabled.widget.setVisible(False)
