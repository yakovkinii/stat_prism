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
