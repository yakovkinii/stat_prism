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

# VALIDATED

from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.iispwac.iispwac_spin import IISPWACSpin
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.cluster_analysis.cluster_analysis_result import ClusterMethod
from src.side_area_panel.modules.common.prose import PROSE_LABEL, PROSE_LEVELS


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Variables:",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=8,
            ),
        ],
    )
    method = IISPWACComboBox(label_text="Method:", items=ClusterMethod.get_values())
    linkage = IISPWACComboBox(label_text="Linkage (hierarchical):", items=["Ward", "Average", "Complete", "Single"])
    n_clusters = IISPWACSpin(label_text="Number of clusters:", min_value=2, max_value=20, default_value=2)
    standardize = IISPWACCheckBox(label_text="Standardize variables (z-score)", default_state=True)
    plots = IISPWACCheckBox(label_text="Plots", default_state=False)
    show_assignments = IISPWACCheckBox(label_text="Show per-observation assignments", default_state=False)
    verbal_indicators = IISPWACCheckBox(label_text="Verbal indicators in tables", default_state=False)
    interpretation = IISPWACComboBox(label_text=PROSE_LABEL, items=PROSE_LEVELS)
    spacer = IISPWACSpacer()


class ClusterAnalysis(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Cluster Analysis")
