#  Copyright (c) 2023 StatPrism Team. All rights reserved.

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


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Variables:",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=10,
            ),
        ],
    )
    method = IISPWACComboBox(label_text="Method:", items=ClusterMethod.get_values())
    n_clusters = IISPWACSpin(label_text="Number of clusters:", min_value=2, max_value=20, default_value=2)
    standardize = IISPWACCheckBox(label_text="Standardize variables (z-score)", default_state=True)
    plots = IISPWACCheckBox(label_text="Plots", default_state=True)
    show_assignments = IISPWACCheckBox(label_text="Show per-observation assignments", default_state=True)
    verbal_indicators = IISPWACCheckBox(label_text="Verbal indicators in tables", default_state=True)
    spacer = IISPWACSpacer()


class ClusterAnalysis(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Cluster Analysis")
