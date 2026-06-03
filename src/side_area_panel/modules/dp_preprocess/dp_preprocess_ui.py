#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_column_editor import IISPWACColumnEditor
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.modules.base.base import BaseModulePanel


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    columns = IISPWACColumnEditor()


class Preprocess(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Preprocess")
