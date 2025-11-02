#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import logging

from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.progress import run_in_separate_thread
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.column_selector import ColumnSelectorEx, Field
from src.pyside_ext.elements.combo_box import ComboBox
from src.pyside_ext.elements.filter import CompiledFilterHistory
from src.pyside_ext.elements.spacer_small import SpacerSmall
from src.pyside_ext.elements.spin import Spin
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.cluster_analysis.main import (
    recalculate_cluster_analysis_study,
)
from src.side_area_panel.modules.cluster_analysis.result import (
    ClusterAnalysisConfig,
    ClusterMethod,
)
from src.side_area_panel.modules.common.result.registry import RESULTS


class ClusterAnalysis(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "method": ComboBox(label_text="Method:"),
            "n_clusters": Spin(label_text="Number of clusters:", min_value=2, max_value=20),
            "spacer2": SpacerSmall(),
            "column_selector": ColumnSelectorEx(
                fields=[
                    Field(
                        name="Variables:",
                        column_type=ColumnType.ORDINAL,
                        reasonable_number_of_columns=10,
                    ),
                ],
            ),
            "compiled_filters": CompiledFilterHistory(),
        }
        self.setup(stretch=True, label="Cluster Analysis")
        self.elements["method"].configure(ClusterMethod.get_values())

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id
        cfg = RESULTS[result_id].config
        self.elements["method"].combo_box.setCurrentText(cfg.method.value)
        self.elements["n_clusters"].spin_box.setValue(cfg.n_clusters)
        self.elements["column_selector"].configure(
            columns=DATA_MANAGER.get_latest_data().get_all_columns_as_column_types(),
            selected_columns_list=[cfg.columns],
        )
        self.elements["compiled_filters"].configure(cfg.filters)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)
        self.configuring = False

    def recalculate(self):
        if self.configuring:
            return
        RESULTS[self.result_id].config = ClusterAnalysisConfig(
            columns=self.elements["column_selector"].get_selected_columns()[0],
            n_clusters=self.elements["n_clusters"].spin_box.value(),
            method=ClusterMethod(self.elements["method"].combo_box.currentText()),
            filters=RESULTS[self.result_id].config.filters,
        )
        data = DATA_MANAGER.get_latest_data()
        result = RESULTS[self.result_id]

        def main(update):
            try:
                return recalculate_cluster_analysis_study(data=data, result=result)
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
