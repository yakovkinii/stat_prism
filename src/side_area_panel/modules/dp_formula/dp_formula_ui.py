#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel


class Elements(ItemInSidePanelWithAutoConfigHolder):
    # No column selector: the formula references columns by name.
    data_source = IISPWACDataSource()
    spacer = IISPWACSpacer()
    new_name = IISPWACLongTextEdit(label_text="New column name:")
    formula = IISPWACLongTextEdit(label_text="Formula (pandas eval. E.g. colA+colB; `col A`/`col B`):")


class Formula(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Formula Column")
