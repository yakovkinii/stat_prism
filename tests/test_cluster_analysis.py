#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot tests for the Cluster Analysis module.

K-means and PCA are seeded (random_state=0) inside the module, so results are
deterministic.
"""

import pytest

from src.side_area_panel.modules.cluster_analysis.cluster_analysis_main import (
    recalculate_cluster_analysis_study,
)
from src.side_area_panel.modules.cluster_analysis.cluster_analysis_result import (
    ClusterAnalysisConfig,
    ClusterAnalysisResult,
    ClusterMethod,
)
from tests.datasets import COL_AGE, COL_INCOME, COL_SATISFACTION, COL_SCORE, MAIN
from tests.helpers import assert_snapshot, load_dataset, run_main

_ITEMS = [COL_AGE, COL_INCOME, COL_SCORE, COL_SATISFACTION]
_KMEANS = ClusterMethod.KMEANS.value
_HIER = ClusterMethod.HIERARCHICAL.value


def _config(**overrides):
    base = dict(
        data_source="Auto",
        column_selector=[_ITEMS],
        method=_KMEANS,
        linkage="Ward",
        n_clusters=3,
        standardize=True,
        plots=False,
        show_assignments=False,
        verbal_indicators=True,
    )
    base.update(overrides)
    return ClusterAnalysisConfig(**base)


CASES = [
    ("cluster_kmeans_3", dict()),
    ("cluster_kmeans_2", dict(n_clusters=2)),
    ("cluster_kmeans_4", dict(n_clusters=4)),
    ("cluster_kmeans_no_standardize", dict(standardize=False)),
    ("cluster_kmeans_assignments", dict(show_assignments=True)),
    ("cluster_hierarchical_ward", dict(method=_HIER, linkage="Ward")),
    ("cluster_hierarchical_complete", dict(method=_HIER, linkage="Complete")),
    ("cluster_hierarchical_average", dict(method=_HIER, linkage="Average")),
]


@pytest.mark.parametrize("name,overrides", CASES, ids=[c[0] for c in CASES])
def test_cluster(name, overrides):
    result = run_main(recalculate_cluster_analysis_study, ClusterAnalysisResult, _config(**overrides), load_dataset(MAIN))
    assert_snapshot(result, name)
