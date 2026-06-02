#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.modules.base.base import BaseModulePanel


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()


class RowId(BaseModulePanel):
    # No user inputs -> compute the ID column automatically once created.
    recalculate_on_create = True

    def setup_ui(self):
        self.elements_ = Elements().complete_init_of_items(
            parent_widget=self.widget_for_elements,
            parent_layout=self.widget_for_elements_layout,
            handler_on_recalculate=self.recalculate,
            stretch=True,
        )
        self.set_label("Row ID")
