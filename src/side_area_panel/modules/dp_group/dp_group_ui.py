#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.dp_group.dp_group_result import SPLIT_SIDES


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()

    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Column:",
                column_type=ColumnType.NUMERIC,
                reasonable_number_of_columns=1,
                allow_only_single_column=True,
                minimum_columns=1,
            ),
        ],
    )

    thresholds = IISPWACLongTextEdit(label_text="Split points (e.g. 30, 60):")
    split_side = IISPWACComboBox(label_text="Split point goes to:", items=SPLIT_SIDES)
    names = IISPWACLongTextEdit(label_text="Group names (optional, comma-separated):")
    new_name = IISPWACLongTextEdit(label_text="New column name (optional):")


class GroupValues(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Group Values")
