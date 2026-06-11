#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.modules.base.base import BaseModulePanel


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Variable 1:",
                column_type=ColumnType.NOMINAL,
                reasonable_number_of_columns=1,
                allow_only_single_column=True,
                minimum_columns=1,
            ),
            Field(
                name="Variable 2:",
                column_type=ColumnType.NOMINAL,
                reasonable_number_of_columns=1,
                allow_only_single_column=True,
                minimum_columns=1,
            ),
        ],
    )
    spacer = IISPWACSpacer()
    continuity_correction = IISPWACCheckBox(
        label_text="Continuity correction",
        default_state=True,
    )
    effect_size = IISPWACCheckBox(
        label_text="Effect size",
        default_state=True,
    )
    verbal_indicators = IISPWACCheckBox(
        label_text="Verbal indicators in tables",
        default_state=True,
    )
    plots = IISPWACCheckBox(
        label_text="Plot",
        default_state=True,
    )


class Contingency(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Contingency Table")
