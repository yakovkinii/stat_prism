#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.modules.base.base import BaseModulePanel


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()

    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Columns:",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=10,
                allow_only_single_column=False,
                minimum_columns=1,
            ),
        ],
    )

    method = IISPWACComboBox(label_text="Method:", items=["IQR", "Z-score"])
    enabled = IISPWACCheckBox(label_text="Enable", default_state=True)


class Outliers(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Outliers")
        # The enable/disable control is the toggle on the result card.
        self.elements_.enabled.widget.setVisible(False)
