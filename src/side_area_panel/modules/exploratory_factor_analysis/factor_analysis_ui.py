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


from PySide6.QtWidgets import QPushButton

from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.iispwac.iispwac_spin import IISPWACSpin
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.prose import PROSE_LABEL, PROSE_LEVELS
from src.side_area_panel.modules.common.result.registry import RESULTS, get_unique_result_id
from src.side_area_panel.modules.confirmatory_factor_analysis.cfa_semopy import OBJECTIVE_DWLS, OBJECTIVE_ML
from src.side_area_panel.modules.exploratory_factor_analysis.exploratory_factor_analysis_result import (
    CORRELATION_METHODS,
    ExtractionMethod,
    RotationType,
)
from src.side_area_panel.modules.registry import ModuleRegistry


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
    correlation_method = IISPWACComboBox(label_text="Correlation:", items=CORRELATION_METHODS)
    method = IISPWACComboBox(label_text="Method:", items=ExtractionMethod.get_values())
    rotation = IISPWACComboBox(label_text="Rotation:", items=RotationType.get_values())
    n_factors = IISPWACSpin(label_text="Number of factors:", min_value=1, max_value=100, default_value=2)
    factor_names = IISPWACLongTextEdit(label_text="Factor names (comma-separated, optional):")
    kaiser_normalization = IISPWACCheckBox(label_text="Kaiser normalization", default_state=True)
    verbal_indicators = IISPWACCheckBox(label_text="Verbal indicators in tables", default_state=False)
    show_item_msa = IISPWACCheckBox(label_text="Show per-item MSA", default_state=False)
    show_eigenvalues = IISPWACCheckBox(label_text="Show eigenvalues table", default_state=False)
    number_columns = IISPWACCheckBox(label_text="Number variables in tables", default_state=False)
    interpretation = IISPWACComboBox(label_text=PROSE_LABEL, items=PROSE_LEVELS)
    plots = IISPWACCheckBox(label_text="Plots", default_state=False)
    spacer = IISPWACSpacer()


class FactorAnalysis(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Exploratory Factor Analysis")
        # At the end: spin off a CFA pre-configured from this EFA's solution (same items and factor
        # count; items assigned to the factor they load highest on; factor correlation if oblique).
        self.make_cfa_button = QPushButton("Create a CFA from this solution", self.widget_for_elements)
        self.make_cfa_button.clicked.connect(self._create_cfa)
        self.widget_for_elements_layout.addWidget(self.make_cfa_button)

    def _create_cfa(self):
        result = RESULTS.get(self.result_id)
        if result is None:
            return
        loadings = getattr(result, "efa_loadings", None)
        columns = getattr(result, "efa_columns", None)
        if not loadings or not columns:
            return  # run the EFA first so its loadings are available

        efa_config = result.config
        n_factors = len(loadings[0]) if loadings and loadings[0] else 0
        if n_factors == 0:
            return
        # Assign each item to the factor it loads on most strongly (by absolute loading).
        structure = [[] for _ in range(n_factors)]
        for row, name in zip(loadings, columns):
            best = max(range(n_factors), key=lambda j: abs(row[j]))
            structure[best].append(name)

        module = ModuleRegistry.CFA.value
        config = module.config_class()
        config.data_source = getattr(efa_config, "data_source", None) or "Auto"
        config.n_factors = n_factors
        config.column_selector = structure
        config.allow_factor_correlation = bool(getattr(result, "efa_is_oblique", False))
        config.second_order = False
        # Ordinal EFA (polychoric correlations) -> DWLS in the CFA; otherwise ML.
        config.estimator = (
            OBJECTIVE_DWLS if getattr(efa_config, "correlation_method", None) == "Polychoric" else OBJECTIVE_ML
        )

        result_id = get_unique_result_id()
        RESULTS[result_id] = module.result_class(
            unique_id=result_id,
            settings_panel_index=module.settings_stacked_widget_index,
            config=config,
        )
        self.root_class.main_area_panel.add_data_analysis(result_id)
        module.ui_instance.configure(result_id)
        module.ui_instance.recalculate()
        # Properly select the new CFA: show its settings panel (not the EFA one) and focus its card.
        self.root_class.main_area_panel.activate_result(result_id, None)
