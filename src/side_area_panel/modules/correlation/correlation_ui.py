#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.correlation.correlation_result import CORRELATION_TYPE_MAP


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Variables:",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=8,
                minimum_columns=2,
            ),
            Field(
                name="Control for (partial, optional):",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=2,
            ),
            Field(
                name="Second variable set (cross, optional):",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=4,
            ),
        ],
    )
    spacer = IISPWACSpacer()
    correlation_type = IISPWACComboBox(
        label_text="Correlation type: ",
        items=list(CORRELATION_TYPE_MAP.keys()),
    )
    compact = IISPWACCheckBox(label_text="Compact table", default_state=True)
    show_interpretation = IISPWACCheckBox(label_text="Verbal report (interpretation)", default_state=False)
    number_columns = IISPWACCheckBox(label_text="Number columns in tables", default_state=False)
    confidence_intervals = IISPWACCheckBox(label_text="95% confidence intervals", default_state=False)
    report_only_significant = IISPWACCheckBox(
        label_text="Report/plot only significant correlations",
        default_state=True,
    )
    generate_heatmap = IISPWACCheckBox(label_text="Heatmap", default_state=False)
    generate_plots = IISPWACCheckBox(label_text="Pairwise plots", default_state=False)


class Correlation(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Correlation")
