#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.modules.base.base import BaseModulePanel


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Dependent Variable:",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=1,
                allow_only_single_column=True,
            ),
            Field(
                name="Independent Variable(s):",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=5,
            ),
            Field(
                name="Moderator Variable (optional):",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=1,
                allow_only_single_column=True,
            ),
            Field(
                name="Mediator Variable (optional):",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=1,
                allow_only_single_column=True,
            ),
        ],
    )
    spacer = IISPWACSpacer()


class Regression(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Regression Analysis")
