#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_filter import IISPWACFilter
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.correlation.result import CORRELATION_TYPE_MAP


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
    spacer = IISPWACSpacer()
    correlation_type = IISPWACComboBox(
        label_text="Correlation type: ",
        items=list(CORRELATION_TYPE_MAP.keys()),
    )
    compact = IISPWACCheckBox(label_text="Compact table", default_state=False)
    report_only_significant = IISPWACCheckBox(
        label_text="Report only significant correlations",
        default_state=True,
    )
    generate_heatmap = IISPWACCheckBox(label_text="Heatmap", default_state=False)
    generate_plots = IISPWACCheckBox(label_text="Pairwise plots", default_state=False)
    filters = IISPWACFilter()


class Correlation(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Correlations")
