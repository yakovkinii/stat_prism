#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_cross_loading_list import IISPWACCrossLoadingList
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.iispwac.iispwac_spin import IISPWACSpin
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.prose import PROSE_LABEL, PROSE_LEVELS
from src.side_area_panel.modules.common.result.registry import RESULTS
from src.side_area_panel.modules.confirmatory_factor_analysis.cfa_semopy import OBJECTIVES


def _make_factor_fields(n_factors: int):
    return [
        Field(
            name=f"Factor {i + 1} variables:",
            column_type=ColumnType.ORDINAL,
            reasonable_number_of_columns=3,
        )
        for i in range(n_factors)
    ]


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    n_factors = IISPWACSpin(label_text="Number of factors:", min_value=1, max_value=20, default_value=2)
    column_selector = IISPWACColumnSelector(fields=_make_factor_fields(2))
    estimator = IISPWACComboBox(label_text="Estimator:", items=OBJECTIVES)
    allow_factor_correlation = IISPWACCheckBox(
        label_text="Allow factor correlation (oblique)",
        default_state=True,
    )
    second_order = IISPWACCheckBox(
        label_text="Second-order factor (≥3 factors)",
        default_state=False,
    )
    verbal_indicators = IISPWACCheckBox(
        label_text="Verbal indicators in tables",
        default_state=False,
    )
    modification_hints = IISPWACCheckBox(label_text="Modification hints (cross-loadings)", default_state=False)
    cross_loadings = IISPWACCrossLoadingList()
    interpretation = IISPWACComboBox(label_text=PROSE_LABEL, items=PROSE_LEVELS)
    number_columns = IISPWACCheckBox(label_text="Number variables in tables", default_state=False)
    plots = IISPWACCheckBox(label_text="Plots", default_state=False)
    spacer = IISPWACSpacer()


class ConfirmatoryFactorAnalysis(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Confirmatory Factor Analysis")
        self.elements_.n_factors.set_handler_value_changed(self._sync_factor_fields)

    def _sync_factor_fields(self):
        n = self.elements_.n_factors.spin_box.value()
        if len(self.elements_.column_selector.fields) != n:
            self.elements_.column_selector.change_fields(_make_factor_fields(n))

    def configure(self, result_id: int):
        n = RESULTS[result_id].config.n_factors or self.elements_.n_factors.default_value
        if len(self.elements_.column_selector.fields) != n:
            self.elements_.column_selector.change_fields(_make_factor_fields(n))
        super().configure(result_id)
