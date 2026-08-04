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


from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_bootstrap_editor import IISPWACBootstrapColumnEditor
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.iispwac.iispwac_spin import IISPWACSpin
from src.side_area_panel.modules.base.base import BaseModulePanel


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Columns to bootstrap:",
                column_type=ColumnType.NOMINAL,
                reasonable_number_of_columns=8,
            ),
            Field(
                name="Drivers (correlate with reference):",
                column_type=ColumnType.NOMINAL,
                reasonable_number_of_columns=8,
            ),
            Field(
                name="Reference (anchor):",
                column_type=ColumnType.NOMINAL,
                reasonable_number_of_columns=1,
                allow_only_single_column=True,
            ),
        ],
    )
    n_rows = IISPWACSpin(label_text="Rows to add:", min_value=0, max_value=100000, default_value=0)
    seed = IISPWACSpin(label_text="Random seed:", min_value=0, max_value=1000000, default_value=0)
    spacer = IISPWACSpacer()
    column_configs = IISPWACBootstrapColumnEditor()


class Bootstrap(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Bootstrap Sensitivity")
