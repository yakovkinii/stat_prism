#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import numpy as np
from sklearn.cluster import KMeans

from src.common.decorators import log_function
from src.common.translations import t
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.cluster_analysis.cluster_analysis_result import (
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
        result.set_placeholder(t("cluster.msg.select_variable"))
        return result
    df = df.select_dtypes(include=[np.number]).astype(float)
    df = df.dropna(axis=0)
    n_rows, n_cols = df.shape
    if n_rows < cfg.n_clusters:
        result.set_placeholder(t("cluster.msg.not_enough", n=cfg.n_clusters))
        return result
    X = df.values
    if method == ClusterMethod.KMEANS:
        kmeans = KMeans(n_clusters=cfg.n_clusters, n_init=10, random_state=0)
        labels = kmeans.fit_predict(X)
        centroids = kmeans.cluster_centers_
    else:
        result.set_placeholder(t("cluster.msg.method_not_implemented"))
        return result
    # Cluster assignment table
    assign_table = HTMLTableV2(table_caption=t("cluster.caption.assignments"))
    assign_table.add_single_row_apa(Row([Cell(t("cluster.col.observation")), Cell(t("cluster.col.cluster"))]))
    for i, label in enumerate(labels):
        assign_table.add_single_row_apa(Row([Cell(str(i + 1)), Cell(str(label + 1))]))
    # Centroid table
    centroid_table = HTMLTableV2(table_caption=t("cluster.caption.centroids"))
    headers = [Cell(t("cluster.col.cluster"))] + [Cell(col) for col in df.columns]
    centroid_table.add_single_row_apa(Row(headers))
    for i, centroid in enumerate(centroids):
        row = [Cell(str(i + 1))] + [Cell(f"{v:.3f}") for v in centroid]
        centroid_table.add_single_row_apa(Row(row))
    result.result_elements = [assign_table, centroid_table]
    result.header = ""
    result.add_header_info(t("cluster.header", method=cfg.method, n=cfg.n_clusters))
    return result
