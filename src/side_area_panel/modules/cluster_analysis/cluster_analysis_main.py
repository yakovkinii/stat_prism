#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import logging

import numpy as np
from scipy.cluster.hierarchy import fcluster
from scipy.cluster.hierarchy import linkage as scipy_linkage
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from src.common.decorators import log_function
from src.common.qcolor import Colors
from src.common.translations import t
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.cluster_analysis.cluster_analysis_result import ClusterAnalysisResult, ClusterMethod
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.result.plot_result import (
    Dendrogram,
    Line,
    LinePlotConfig,
    PlotV2,
    Scatter,
    ScatterPlotConfig,
)
from src.side_area_panel.modules.common.utility import format_r_apa, format_statistic_apa, format_value_apa


def _fail(result: ClusterAnalysisResult, message: str) -> ClusterAnalysisResult:
    """Show a validation message to the user and log it, then stop."""
    logging.warning("Cluster: %s", message)
    result.set_error(message)
    return result


def _silhouette_key(score: float) -> str:
    if score > 0.7:
        return "strong"
    if score > 0.5:
        return "reasonable"
    if score > 0.25:
        return "weak"
    return "none"


@log_function
def recalculate_cluster_analysis_study(elements, result: ClusterAnalysisResult, update) -> ClusterAnalysisResult:
    """Validate inputs, run K-means (optionally on standardised variables), and report the
    cluster sizes + centroids, a silhouette quality score, a 2-D cluster scatter and the
    per-observation assignments. `update(pct)` drives the progress bar. Unexpected exceptions
    are handled centrally by the panel's recalculate()."""
    cfg = result.config
    result.result_elements = []

    method = ClusterMethod(cfg.method)

    selected = cfg.column_selector[0]
    if not selected:
        return _fail(result, t("cluster.msg.select_variable"))
    update(5)

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )

    # Ordinal items are scored numerically so Likert scales are usable.
    df = data.get_dataframe(columns=selected, map_ordinal=True)
    df = df.select_dtypes(include=[np.number]).astype(float).dropna(axis=0)
    n_rows, n_cols = df.shape
    if n_cols < 1:
        return _fail(result, t("cluster.msg.select_variable"))
    k = cfg.n_clusters
    if n_rows < k:
        return _fail(result, t("cluster.msg.not_enough", n=k))

    columns = list(df.columns)
    original = df.values
    standardize = bool(cfg.standardize)
    verbal = bool(cfg.verbal_indicators)

    # K-means uses Euclidean distance, so optionally z-score the variables first.
    if standardize:
        std = original.std(axis=0, ddof=0)
        std[std == 0] = 1.0
        x = (original - original.mean(axis=0)) / std
    else:
        x = original

    update(10)
    linkage_method = (cfg.linkage or "Ward").lower()
    linkage_matrix = None
    inertia = None
    if method == ClusterMethod.HIERARCHICAL:
        linkage_matrix = scipy_linkage(x, method=linkage_method)
        labels = fcluster(linkage_matrix, t=k, criterion="maxclust") - 1
    else:
        kmeans = KMeans(n_clusters=k, n_init=10, random_state=0)
        labels = kmeans.fit_predict(x)
        inertia = kmeans.inertia_
    counts = np.bincount(labels, minlength=k)
    update(25)

    try:
        silhouette = silhouette_score(x, labels) if len(np.unique(labels)) > 1 else float("nan")
    except Exception:  # pragma: no cover - defensive
        silhouette = float("nan")
    update(30)

    # ----- Centroids (in original units) + sizes + prose -----
    centroid_table = HTMLTableV2(table_caption=t("cluster.caption.centroids"))
    centroid_table.add_title_row_apa(
        Row(
            [
                Cell(t("cluster.col.cluster")),
                Cell(t("cluster.col.size"), center=True),
                Cell(t("cluster.col.percent"), center=True),
            ]
            + [Cell(col, center=True) for col in columns]
        )
    )
    for c in range(k):
        cluster_original = original[labels == c]
        centroid = cluster_original.mean(axis=0) if cluster_original.size else np.full(n_cols, np.nan)
        centroid_table.add_single_row_apa(
            Row(
                [
                    Cell(str(c + 1), push_to_left=True),
                    Cell(str(int(counts[c])), center=True),
                    Cell(format_value_apa(100.0 * counts[c] / n_rows, 1), center=True),
                ]
                + [Cell(format_statistic_apa(v, 2), center=True) for v in centroid]
            )
        )

    report = t("cluster.report.summary", k=k, sizes=", ".join(str(int(s)) for s in counts))
    report += t("cluster.report.standardized") if standardize else t("cluster.report.unstandardized")
    if not np.isnan(silhouette):
        report += t(
            "cluster.report.silhouette",
            sil=format_r_apa(silhouette),
            label=t(f"cluster.sil.{_silhouette_key(silhouette)}"),
        )
    verbal and centroid_table.add_text(report)
    result.update_and_add_element(centroid_table, "cluster centroids")

    # ----- Quality table -----
    quality_table = HTMLTableV2(table_caption=t("cluster.caption.quality"))
    quality_header = [Cell(t("cluster.col.metric")), Cell(t("cluster.col.value"), center=True)]
    if verbal:
        quality_header.append(Cell(t("cluster.col.interpretation"), center=True))
    quality_table.add_title_row_apa(Row(quality_header))

    silhouette_cells = [
        Cell(t("cluster.metric.silhouette"), push_to_left=True),
        Cell(format_r_apa(silhouette), center=True),
    ]
    if verbal:
        silhouette_cells.append(
            Cell(t(f"cluster.sil.{_silhouette_key(silhouette)}") if not np.isnan(silhouette) else "—", center=True)
        )
    quality_table.add_single_row_apa(Row(silhouette_cells))

    if inertia is not None:
        inertia_cells = [
            Cell(t("cluster.metric.inertia"), push_to_left=True),
            Cell(format_statistic_apa(inertia, 1), center=True),
        ]
        if verbal:
            inertia_cells.append(Cell("—", center=True))
        quality_table.add_single_row_apa(Row(inertia_cells))
    result.update_and_add_element(quality_table, "cluster quality")

    # ----- Plots: k-selection sweep, dendrogram (hierarchical), 2-D scatter -----
    if cfg.plots:
        # The k-selection sweep refits the model for k=2..10, so it is the slow part: report
        # per-k progress across 30 -> 85.
        for i, plot in enumerate(_k_selection_plots(x, method, linkage_method, linkage_matrix, n_rows, update, 30, 85)):
            result.update_and_add_element(plot, f"cluster kselect {i}")
        if linkage_matrix is not None:
            result.update_and_add_element(_dendrogram_plot(linkage_matrix), "cluster dendrogram")
        scatter_plot = _build_scatter(x, original, labels, k, columns)
        if scatter_plot is not None:
            result.update_and_add_element(scatter_plot, "cluster scatter")
    update(90)

    # ----- Per-observation assignments (optional; can be large) -----
    if cfg.show_assignments:
        assign_table = HTMLTableV2(table_caption=t("cluster.caption.assignments"))
        assign_table.add_title_row_apa(
            Row([Cell(t("cluster.col.observation")), Cell(t("cluster.col.cluster"), center=True)])
        )
        for id_label, label in zip(data.get_id_series(), labels):
            assign_table.add_single_row_apa(Row([Cell(id_label, push_to_left=True), Cell(str(label + 1), center=True)]))
        result.update_and_add_element(assign_table, "cluster assignments")

    update(100)
    result.title_context = f"{k} clusters"
    return result


def _build_scatter(x: np.ndarray, original: np.ndarray, labels: np.ndarray, k: int, columns):
    """One scatter series per cluster in two dimensions: the two variables directly (in
    their original units) when exactly two are selected, otherwise the first two principal
    components of the clustered (possibly standardised) space."""
    n_cols = x.shape[1]
    if n_cols < 2:
        return None

    if n_cols == 2:
        coords = original
        x_title, y_title = columns[0], columns[1]
    else:
        pca = PCA(n_components=2, random_state=0)
        coords = pca.fit_transform(x)
        variance = pca.explained_variance_ratio_ * 100.0
        x_title = t("cluster.plot.pc", n=1, pct=format_value_apa(variance[0], 1))
        y_title = t("cluster.plot.pc", n=2, pct=format_value_apa(variance[1], 1))

    colors = Colors()
    items = []
    for c in range(k):
        mask = labels == c
        if not np.any(mask):
            continue
        label = t("cluster.plot.cluster_label", n=c + 1)
        items.append(
            Scatter(
                x=coords[mask, 0],
                y=coords[mask, 1],
                label=label,
                legend_string=label,
                config=ScatterPlotConfig(color=colors.get_color_list()),
            )
        )

    return PlotV2(
        items=items,
        title=t("cluster.plot.scatter"),
        plot_title=t("cluster.plot.scatter"),
        x_axis_title=x_title,
        y_axis_title=y_title,
    )


def _k_selection_plots(x, method, linkage_method, linkage_matrix, n_rows, update, lo, hi):
    """Sweep k = 2..min(10, n-1): mean silhouette for the chosen method (both methods), and
    the K-means inertia 'elbow' (K-means only), to help choose the number of clusters.
    Reports progress across [lo, hi] as the sweep proceeds."""
    max_k = min(10, n_rows - 1)
    if max_k < 2:
        return []
    ks = list(range(2, max_k + 1))
    silhouettes = []
    inertias = []
    for step, candidate_k in enumerate(ks):
        if method == ClusterMethod.HIERARCHICAL:
            labels_k = fcluster(linkage_matrix, t=candidate_k, criterion="maxclust") - 1
        else:
            model_k = KMeans(n_clusters=candidate_k, n_init=10, random_state=0)
            labels_k = model_k.fit_predict(x)
            inertias.append(model_k.inertia_)
        try:
            sil = silhouette_score(x, labels_k) if len(np.unique(labels_k)) > 1 else float("nan")
        except Exception:  # pragma: no cover - defensive
            sil = float("nan")
        silhouettes.append(sil)
        update(lo + (hi - lo) * (step + 1) / len(ks))

    colors = Colors()
    ks_arr = np.array(ks, dtype=float)
    plots = []

    sil_color = colors.get_color_list()
    plots.append(
        PlotV2(
            items=[
                Line(
                    x=ks_arr,
                    y=np.array(silhouettes, dtype=float),
                    label=t("cluster.metric.silhouette"),
                    legend_string=t("cluster.metric.silhouette"),
                    config=LinePlotConfig(color=sil_color),
                ),
                Scatter(x=ks_arr, y=np.array(silhouettes, dtype=float), label=t("cluster.metric.silhouette")),
            ],
            title=t("cluster.plot.kselect_sil"),
            plot_title=t("cluster.plot.kselect_sil"),
            x_axis_title=t("cluster.plot.k"),
            y_axis_title=t("cluster.metric.silhouette"),
        )
    )

    if inertias:  # K-means elbow
        inertia_color = colors.get_color_list()
        plots.append(
            PlotV2(
                items=[
                    Line(
                        x=ks_arr,
                        y=np.array(inertias, dtype=float),
                        label=t("cluster.metric.inertia"),
                        legend_string=t("cluster.metric.inertia"),
                        config=LinePlotConfig(color=inertia_color),
                    ),
                    Scatter(x=ks_arr, y=np.array(inertias, dtype=float), label=t("cluster.metric.inertia")),
                ],
                title=t("cluster.plot.kselect_inertia"),
                plot_title=t("cluster.plot.kselect_inertia"),
                x_axis_title=t("cluster.plot.k"),
                y_axis_title=t("cluster.metric.inertia"),
            )
        )

    return plots


def _dendrogram_plot(linkage_matrix):
    """Dendrogram of the agglomerative linkage (rendered by the Dendrogram plot item)."""
    return PlotV2(
        items=[Dendrogram(linkage_matrix=linkage_matrix, label=t("cluster.plot.dendrogram"))],
        title=t("cluster.plot.dendrogram"),
        plot_title=t("cluster.plot.dendrogram"),
        x_axis_title=t("cluster.plot.observations"),
        y_axis_title=t("cluster.plot.distance"),
    )
