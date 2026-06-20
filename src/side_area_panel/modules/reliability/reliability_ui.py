#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.correlation.correlation_result import CORRELATION_TYPE_MAP


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Underlying Questions:",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=10,
                minimum_columns=2,
            ),
        ],
    )
    spacer = IISPWACSpacer()
    correlation_type = IISPWACComboBox(
        label_text="Correlation type: ",
        items=list(CORRELATION_TYPE_MAP.keys()),
    )
    scale_name = IISPWACLongTextEdit(label_text="Scale name (optional):")
    mcdonald_omega = IISPWACCheckBox(label_text="McDonald's ω", default_state=True)
    verbal_indicators = IISPWACCheckBox(label_text="Verbal indicators in tables", default_state=True)
    number_columns = IISPWACCheckBox(label_text="Number items in tables", default_state=False)


class Reliability(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Reliability")
