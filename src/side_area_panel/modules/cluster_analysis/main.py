#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import numpy as np
from sklearn.cluster import KMeans

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.cluster_analysis.result import (
    ClusterAnalysisResult,
    ClusterMethod,
)
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row


@log_function
def recalculate_cluster_analysis_study(elements, result: ClusterAnalysisResult) -> ClusterAnalysisResult:
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    method = ClusterMethod(cfg.method)
    df = data.get_dataframe(columns=cfg.column_selector[0], map_ordinal=False)
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
    if method == ClusterMethod.KMEANS:
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
        assign_table.add_single_row_apa(Row([Cell(str(i + 1)), Cell(str(label + 1))]))
    # Centroid table
    centroid_table = HTMLTableV2(table_caption="Cluster Centroids")
    headers = [Cell("Cluster")] + [Cell(col) for col in df.columns]
    centroid_table.add_single_row_apa(Row(headers))
    for i, centroid in enumerate(centroids):
        row = [Cell(str(i + 1))] + [Cell(f"{v:.3f}") for v in centroid]
        centroid_table.add_single_row_apa(Row(row))
    result.result_elements = [assign_table, centroid_table]
    result.header = ""
    result.add_header_info(f"Method: <i>{cfg.method}</i>; Clusters: <i>{cfg.n_clusters}</i>")
    return result
