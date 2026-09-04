#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.


from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_column_reorder_list import IISPWACColumnReorderList
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.modules.base.base import BaseModulePanel


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    order = IISPWACColumnReorderList()


class ArrangeColumns(BaseModulePanel):
    # Compute on create so the step passes data through (in the default order) right away, even
    # before the user drags anything.
    recalculate_on_create = True

    def setup_ui(self):
        # stretch=False so no trailing spacer competes with the reorder list, which expands to
        # fill the whole available panel height.
        self.elements_ = Elements().complete_init_of_items(
            parent_widget=self.widget_for_elements,
            parent_layout=self.widget_for_elements_layout,
            handler_on_recalculate=self.recalculate,
            stretch=False,
        )
        self.set_label("Arrange Columns")
