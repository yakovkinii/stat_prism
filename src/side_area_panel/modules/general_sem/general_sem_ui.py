#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_path_builder import IISPWACPathBuilder
from src.side_area_panel.iispwac.iispwac_spin import IISPWACSpin
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.prose import PROSE_LABEL, PROSE_LEVELS
from src.side_area_panel.modules.common.result.registry import RESULTS
from src.side_area_panel.modules.confirmatory_factor_analysis.cfa_semopy import OBJECTIVES


def _make_factor_fields(n_factors: int):
    return [
        Field(name=f"Factor {i + 1} indicators:", column_type=ColumnType.ORDINAL, reasonable_number_of_columns=3)
        for i in range(n_factors)
    ]


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    # Measurement model: N latent factors, each defined by clicking its observed indicators.
    n_factors = IISPWACSpin(label_text="Number of latent factors:", min_value=1, max_value=20, default_value=2)
    column_selector = IISPWACColumnSelector(fields=_make_factor_fields(2))
    factor_names = IISPWACLongTextEdit(label_text="Factor names (comma-separated, optional):")
    # Structural model: regressions among the factors / observed variables, built click-only.
    paths = IISPWACPathBuilder()
    estimator = IISPWACComboBox(label_text="Estimator:", items=OBJECTIVES)
    verbal_indicators = IISPWACCheckBox(label_text="Verbal indicators in tables", default_state=False)
    interpretation = IISPWACComboBox(label_text=PROSE_LABEL, items=PROSE_LEVELS)
    plots = IISPWACCheckBox(label_text="Path diagram", default_state=False)


class GeneralSEM(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Structural Equation Model")
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
