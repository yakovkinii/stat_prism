from __future__ import annotations

import math

from tests.benchmarks.cluster_analysis.cases import CASES, cluster_data
from tests.benchmarks.cluster_analysis.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE
from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report

MODULE = "cluster_analysis"
RELATIVE_TOLERANCES: dict = {}


def _clean(value):
    if value is None:
        return None
    value = float(value)
    return None if math.isnan(value) else value


def _build_data(df):
    import pandas as pd

    from src.common.constant import ID_COLUMN_NAME, ColumnType
    from src.data.data import Data, DataColumn

    data = Data.initialize_from_dataframe(df)
    # recalculate_cluster_analysis_study reads data.get_id_series(), so the data must carry an ID
    # column exactly as an imported dataset does.
    index = data.columns[0].data_series.index
    id_series = pd.Series(range(1, len(index) + 1), index=index, name=ID_COLUMN_NAME)
    id_column = DataColumn.initialize_from_series(id_series)
    id_column.column_type = ColumnType.ID
    id_column.is_numeric = False
    data.add_column_first(id_column)
    return data


def cluster_payload(case: dict) -> dict:
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.data.data_manager import DATA_MANAGER
    from src.side_area_panel.modules.cluster_analysis.cluster_analysis_main import recalculate_cluster_analysis_study
    from src.side_area_panel.modules.cluster_analysis.cluster_analysis_result import (
        ClusterAnalysisConfig,
        ClusterAnalysisResult,
    )

    cfg = ClusterAnalysisConfig(
        data_source="Auto",
        column_selector=[["x1", "x2"]],
        method=case["method"],
        linkage=case["linkage"],
        n_clusters=case["k"],
        standardize=False,
        plots=False,
        show_assignments=False,
        verbal_indicators=False,
        interpretation=None,
    )
    data = _build_data(cluster_data())
    original = DATA_MANAGER.get_data_from_data_label
    DATA_MANAGER.get_data_from_data_label = lambda *a, **k: data
    try:
        result = ClusterAnalysisResult(unique_id=1, settings_panel_index=0, config=cfg)
        recalculate_cluster_analysis_study(None, result, lambda _p: None)
    finally:
        DATA_MANAGER.get_data_from_data_label = original

    supplements = [s for s in result.numeric_supplements() if s.get("kind") == case["kind"]]
    if not supplements:
        raise AssertionError(f"{case['study']}: no supplement (error={result.error_message!r})")
    s = supplements[0]
    return {
        "error": "",
        "silhouette": _clean(s["silhouette"]),
        "heights": [_clean(h) for h in s["heights"]],
        "clusters": [
            {"size": _clean(c["size"]), "centroid": [_clean(v) for v in c["centroid"]]} for c in s["clusters"]
        ],
    }


def run_case(case: dict, benchmarks: dict) -> BenchmarkCaseResult:
    actual = cluster_payload(case)
    expected = benchmarks["studies"][case["study"]]
    comparisons = compare_payloads(
        actual,
        expected,
        tolerance=benchmarks.get("tolerance", 1e-8),
        relative_tolerance=RELATIVE_TOLERANCES.get(case["study"]),
    )
    return BenchmarkCaseResult(MODULE, case["study"], BENCHMARK_PATH, GENERATOR_PATH, comparisons)


def run_cluster_analysis_benchmarks() -> list[BenchmarkCaseResult]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Missing cluster-analysis R benchmark file: {BENCHMARK_PATH}\n"
            "Run: ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks"
        )
    benchmarks = load_json(BENCHMARK_PATH)
    return [run_case(case, benchmarks) for case in CASES]


def main() -> int:
    results = run_cluster_analysis_benchmarks()
    report = render_report(results, HERE / "cluster_analysis_benchmark_report.html")
    failed = [result for result in results if not result.passed]
    print(f"Cluster-analysis benchmark report written to {report}")
    if failed:
        print(f"{len(failed)} cluster-analysis benchmark study/studies failed.")
        return 1
    print("All cluster-analysis benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
