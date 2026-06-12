#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from enum import Enum

import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


class ClusterMethod(Enum):
    KMEANS = "KMeans"

    @staticmethod
    def get_values():
        return [e.value for e in ClusterMethod]


@attrs.define
class ClusterAnalysisConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    method = attrs.field(default=None)
    n_clusters = attrs.field(default=None)
    standardize = attrs.field(default=None)
    show_assignments = attrs.field(default=None)
    verbal_indicators = attrs.field(default=None)


# Fine-print on the exact methodology / variants this module uses. English only by
# design (only reports/tables are localised), rendered in a smaller font under the
# general description so the chosen conventions are explicit and auditable.
_ASSUMPTIONS_FINE_PRINT_EN = (
    "<b>Methodology &amp; assumptions</b>"
    "<ul>"
    "<li><b>Algorithm.</b> K-means (Lloyd's algorithm, 10 random initialisations, fixed seed "
    "so a re-run reproduces the result). You set the number of clusters k in advance. Rows "
    "with any missing value are dropped (list-wise) and ordinal items are scored numerically.</li>"
    "<li><b>Standardisation.</b> K-means uses Euclidean distance, so variables on larger scales "
    "dominate. &lsquo;Standardise variables&rsquo; z-scores each variable first (recommended "
    "when variables are on different scales); centroids are always reported back in the "
    "original units.</li>"
    "<li><b>Quality.</b> The mean silhouette (&minus;1..1) measures how well each point sits in "
    "its cluster vs the nearest other cluster: &gt; .7 strong, &gt; .5 reasonable, &gt; .25 "
    "weak, otherwise no substantial structure. Inertia is the total within-cluster sum of "
    "squared distances (lower is tighter, but it always falls as k grows).</li>"
    "<li><b>Plot.</b> The scatter shows the clusters in two dimensions: the two variables "
    "directly when exactly two are selected, otherwise the first two principal components "
    "(with the % of variance each captures).</li>"
    "<li><b>Choosing k.</b> K-means does not choose k for you; compare the silhouette across a "
    "few values of k, or use domain knowledge.</li>"
    "</ul>"
)


class ClusterAnalysisResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ClusterAnalysisConfig):
        super().__init__(unique_id)
        self.title = "Cluster Analysis"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = ClusterAnalysisConfig
        self.config: ClusterAnalysisConfig = config
        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("cluster.description")
            + HTML.hr()
            + HTML.div(_ASSUMPTIONS_FINE_PRINT_EN, font_size=Style.FontSize.smaller)
        )
