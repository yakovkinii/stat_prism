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
from src.side_area_panel.iispwac.iispwac_spin import IISPWACSpin
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.cleaning_logic import CHECKS, detect_response_quality


def _detect(data, params):
    columns = (params.get("column_selector") or [[]])[0] or []
    check = params.get("check") or CHECKS[0]
    threshold = params.get("threshold")
    threshold = 50 if threshold is None else threshold
    return detect_response_quality(data, check, columns, threshold)


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()

    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Questions:",
                column_type=ColumnType.NOMINAL,  # any column type may be inspected
                reasonable_number_of_columns=8,
                allow_only_single_column=False,
                minimum_columns=1,
            ),
        ],
    )

    check = IISPWACComboBox(label_text="Check:", items=CHECKS)
    # Shared knob for the percentage-based checks (ignored by "Duplicate entries"):
    # the share of items at which a respondent is flagged.
    threshold = IISPWACSpin(
        label_text="Flag at % of items:",
        min_value=0,
        max_value=100,
        default_value=50,
    )
    remove_list = IISPWACRemoveList(detector=_detect)
    enabled = IISPWACCheckBox(label_text="Enable", default_state=True)


class ResponseQuality(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Response Quality")
        # The enable/disable control is the toggle on the result card.
        self.elements_.enabled.widget.setVisible(False)
