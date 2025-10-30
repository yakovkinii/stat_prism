#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging

from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.progress import run_in_separate_thread
from src.data.data_manager import DATA_MANAGER
from src.modules.base.base import BaseModulePanel
from src.modules.common.result.registry import RESULTS
from src.modules.confirmatory_factor_analysis.main import recalculate_cfa_study
from src.modules.confirmatory_factor_analysis.result import CFAStudyConfig
from src.pyside_ext.elements.checkbox import LargeCheckbox
from src.pyside_ext.elements.column_selector import ColumnSelectorEx, Field
from src.pyside_ext.elements.filter import CompiledFilterHistory
from src.pyside_ext.elements.spacer_small import SpacerSmall
from src.pyside_ext.elements.spin import Spin


class ConfirmatoryFactorAnalysis(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "n_factors": Spin(label_text="Number of factors:", min_value=1, max_value=20),
            "allow_factor_correlation": LargeCheckbox(label_text="Allow factor correlation (oblique)"),
            "spacer2": SpacerSmall(),
            "column_selector": ColumnSelectorEx(fields=[]),
            "compiled_filters": CompiledFilterHistory(),
        }
        self.setup(stretch=True, label="Confirmatory Factor Analysis")

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id
        cfg = RESULTS[result_id].config
        self.elements["n_factors"].spin_box.setValue(cfg.n_factors)
        self.elements["allow_factor_correlation"].widget.setChecked(cfg.allow_factor_correlation)
        n_factors = cfg.n_factors
        # Create fields for each factor
        fields = [
            Field(
                name=f"Factor {i+1} variables:",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=3,
            )
            for i in range(n_factors)
        ]
        self.elements["column_selector"].change_fields(fields=fields)

        # Prepare selected_columns_list for each factor
        if cfg.columns_list:
            if len(cfg.columns_list) >= n_factors:
                selected_columns_list = cfg.columns_list[:n_factors]
            else:
                selected_columns_list = cfg.columns_list + [[] for _ in range(n_factors - len(cfg.columns_list))]
        else:
            selected_columns_list = [[] for _ in range(n_factors)]

        self.elements["column_selector"].configure(
            columns=DATA_MANAGER.get_latest_data().get_all_columns_as_column_types(),
            selected_columns_list=selected_columns_list,
        )
        self.elements["compiled_filters"].configure(cfg.filters)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)
        self.configuring = False

    def recalculate(self):
        if self.configuring:
            return
        n_factors = self.elements["n_factors"].spin_box.value()
        columns_list = self.elements["column_selector"].get_selected_columns()
        RESULTS[self.result_id].config = CFAStudyConfig(
            columns_list=columns_list,
            n_factors=n_factors,
            allow_factor_correlation=self.elements["allow_factor_correlation"].widget.isChecked(),
            filters=RESULTS[self.result_id].config.filters,
        )
        data = DATA_MANAGER.get_latest_data()
        result = RESULTS[self.result_id]

        def main(update):
            try:
                return recalculate_cfa_study(data=data, result=result)
            except Exception as e:
                logging.error(f"Error during calculation: {e}")
                result.set_placeholder("Error during calculation: " + str(e))
                return result

        run_in_separate_thread(
            main, progress_bar=self.root_class.settings_panel.progress_bar, on_done=self.recalculate_on_done
        )

    @log_method
    def recalculate_on_done(self, result):
        RESULTS[self.result_id] = result
        RESULTS[self.result_id].needs_update = False
        self.configure(result_id=self.result_id)
        self.root_class.main_area_panel.refresh_result(result_id=self.result_id)
