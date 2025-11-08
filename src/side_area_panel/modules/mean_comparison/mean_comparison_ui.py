#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.progress import run_in_separate_thread
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.result.registry import RESULTS
from src.side_area_panel.modules.mean_comparison.constant import (
    AssumptionChecksInGrouping,
    MeanComparisonMethod,
    MissingValuesInGrouping,
)
from src.side_area_panel.modules.mean_comparison.mean_comparison_result import (
    MeanComparisonStudyConfig,
)


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Variable(s):",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=10,
                minimum_columns=1,
            ),
            Field(
                name="Grouping Column:",
                column_type=ColumnType.NOMINAL,
                reasonable_number_of_columns=1,
                allow_only_single_column=True,
                minimum_columns=1,
            ),
        ],
    )
    method = IISPWACComboBox(
        label_text="Method:",
        items=MeanComparisonMethod.get_values(),
    )
    grouping_missing = IISPWACComboBox(
        label_text="Missing in grouping:",
        items=MissingValuesInGrouping.get_values(),
    )
    assumption_checks = IISPWACComboBox(
        label_text="Check assumptions:",
        items=AssumptionChecksInGrouping.get_values(),
    )
    effect_size = IISPWACCheckBox(
        label_text="Effect size/Post-hoc",
        default_state=True,
    )
    means = IISPWACCheckBox(
        label_text="Means/Medians",
        default_state=True,
    )
    plots = IISPWACCheckBox(
        label_text="Plots",
        default_state=False,
    )


class MeanComparison(BaseModulePanel):
    def setup_ui(self):
        self.elements_ = Elements().complete_init_of_items(
            parent_widget=self.widget_for_elements,
            parent_layout=self.widget_for_elements_layout,
            handler_on_recalculate=self.recalculate,
            stretch=True,
        )
        self.set_label("T-test/ANOVA")
