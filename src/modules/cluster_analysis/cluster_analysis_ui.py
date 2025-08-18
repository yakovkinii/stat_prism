#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import logging

from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.progress import run_in_separate_thread
from src.data.data_manager import DATA_MANAGER
from src.modules.base.base import BaseModulePanel
from src.modules.common.result.registry import RESULTS
from src.modules.cluster_analysis.main import recalculate_cluster_analysis_study
from src.modules.cluster_analysis.result import (
    ClusterAnalysisConfig,
    ClusterMethod,
)
from src.pyside_ext.elements.checkbox import LargeCheckbox
from src.pyside_ext.elements.column_selector import ColumnSelectorEx, Field
from src.pyside_ext.elements.combo_box import ComboBox
from src.pyside_ext.elements.filter import CompiledFilterHistory
from src.pyside_ext.elements.spacer_small import SpacerSmall
from src.pyside_ext.elements.spin import Spin
from src.pyside_ext.elements.title import Title

class ClusterAnalysis(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Cluster Analysis"),
            "spacer1": SpacerSmall(),
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
        self.setup(stretch=True)
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
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from src.common.decorators import log_function
from src.data.data import Data
from src.modules.common.result.html_result import Cell, HTMLTableV2, Row
from .result import ClusterAnalysisResult, ClusterMethod

@log_function
def recalculate_cluster_analysis_study(data: Data, result: ClusterAnalysisResult) -> ClusterAnalysisResult:
    cfg = result.config
    df = data.get_dataframe(filters=cfg.filters, columns=cfg.columns, map_ordinal=False)
    if df is None or df.shape[1] < 1:
        result.set_placeholder("Select at least one variable.")
        return result
    df = df.select_dtypes(include=[np.number]).astype(float)
    df = df.dropna(axis=0)
    n_rows, n_cols = df.shape
    if n_rows < cfg.n_clusters:
        result.set_placeholder(f"Not enough data for {cfg.n_clusters} clusters.")
        return result
    X = df.values
    if cfg.method == ClusterMethod.KMEANS:
        kmeans = KMeans(n_clusters=cfg.n_clusters, n_init=10, random_state=0)
        labels = kmeans.fit_predict(X)
        centroids = kmeans.cluster_centers_
    else:
        result.set_placeholder("Selected clustering method not implemented.")
        return result
    # Cluster assignment table
    assign_table = HTMLTableV2(table_caption="Cluster Assignments")
    assign_table.add_single_row_apa(Row([Cell("Observation"), Cell("Cluster")]))
    for i, label in enumerate(labels):
        assign_table.add_single_row_apa(Row([Cell(str(i+1)), Cell(str(label+1))]))
    # Centroid table
    centroid_table = HTMLTableV2(table_caption="Cluster Centroids")
    headers = [Cell("Cluster")] + [Cell(col) for col in df.columns]
    centroid_table.add_single_row_apa(Row(headers))
    for i, centroid in enumerate(centroids):
        row = [Cell(str(i+1))] + [Cell(f"{v:.3f}") for v in centroid]
        centroid_table.add_single_row_apa(Row(row))
    result.result_elements = [assign_table, centroid_table]
    result.header = ""
    result.add_header_info(f"Method: <i>{cfg.method.value}</i>; Clusters: <i>{cfg.n_clusters}</i>")
    return result
DESCRIPTION = """
<h2> Cluster Analysis </h2>
<h3> Description </h3>
<div>
Cluster analysis groups observations into clusters based on similarity. This module supports KMeans clustering and reports cluster assignments, centroids, and summary statistics for each cluster.
</div>
<h3> Inputs </h3>
<div>
<b>Variables:</b> Numeric variables to use for clustering.<br>
<b>Number of clusters:</b> How many clusters to form.<br>
<b>Method:</b> KMeans (other methods may be added in the future).<br>
<b>Filters:</b> Data filters to apply.<br>
</div>
"""

