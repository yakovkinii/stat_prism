#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.paired.constant import (
    PairedAssumptionChecks,
    PairedMethod,
)


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Conditions:",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=10,
                minimum_columns=2,
            ),
        ],
    )
    spacer1 = IISPWACSpacer()
    method = IISPWACComboBox(
        label_text="Method:",
        items=PairedMethod.get_values(),
    )
    assumption_checks = IISPWACComboBox(
        label_text="Check assumptions:",
        items=PairedAssumptionChecks.get_values(),
    )
    effect_size = IISPWACCheckBox(
        label_text="Effect size/Post-hoc",
        default_state=True,
    )
    verbal_indicators = IISPWACCheckBox(
        label_text="Verbal indicators in tables",
        default_state=True,
    )
    plots = IISPWACCheckBox(
        label_text="Plots",
        default_state=False,
    )


class Paired(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Paired/Repeated Measures")
