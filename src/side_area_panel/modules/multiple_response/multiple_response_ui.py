#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.modules.base.base import BaseModulePanel


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Indicator columns (0/1):",
                column_type=ColumnType.NUMERIC,
                reasonable_number_of_columns=12,
                minimum_columns=1,
            ),
        ],
    )
    show_chart = IISPWACCheckBox(label_text="Bar chart of counts", default_state=False)
    verbal_indicators = IISPWACCheckBox(label_text="Explanatory note", default_state=False)


class MultipleResponse(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Multiple Response")
