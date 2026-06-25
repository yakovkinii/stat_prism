#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_transform_editor import IISPWACTransformEditor
from src.side_area_panel.modules.base.base import BaseModulePanel


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Column(s):",
                column_type=ColumnType.NOMINAL,
                reasonable_number_of_columns=8,
                minimum_columns=1,
            ),
        ],
    )
    transform_spec = IISPWACTransformEditor()


class Transform(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Transform Column")
