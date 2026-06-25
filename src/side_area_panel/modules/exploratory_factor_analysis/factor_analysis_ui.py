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
from src.side_area_panel.modules.exploratory_factor_analysis.exploratory_factor_analysis_result import (
    ExtractionMethod,
    RotationType,
)


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
    method = IISPWACComboBox(label_text="Method:", items=ExtractionMethod.get_values())
    rotation = IISPWACComboBox(label_text="Rotation:", items=RotationType.get_values())
    n_factors = IISPWACSpin(label_text="Number of factors:", min_value=1, max_value=100, default_value=2)
    kaiser_normalization = IISPWACCheckBox(label_text="Kaiser normalization", default_state=True)
    number_columns = IISPWACCheckBox(label_text="Number variables in tables", default_state=False)
    plots = IISPWACCheckBox(label_text="Plots", default_state=False)
    spacer = IISPWACSpacer()


class FactorAnalysis(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Exploratory Factor Analysis")
