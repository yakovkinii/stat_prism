from __future__ import annotations

import math

from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report
from tests.benchmarks.descriptives.cases import CASES
from tests.benchmarks.descriptives.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE

MODULE = "descriptives"
RELATIVE_TOLERANCES: dict = {}

SUMMARY_KEYS = ("N", "missing", "mean", "std", "se", "median", "q1", "q3", "skew", "kurtosis", "min", "max")


def _clean(value):
    value = float(value)
    return None if math.isnan(value) else value


def _build_data(df):
    import pandas as pd

    from src.common.constant import ID_COLUMN_NAME, ColumnType
    from src.data.data import Data, DataColumn

    data = Data.initialize_from_dataframe(df)
    # recalculate_descriptive_study reads the dataframe with include_id_column=True (for the outlier
    # ID list), so the data must carry an ID column, exactly as an imported dataset does.
    index = data.columns[0].data_series.index
    id_series = pd.Series(range(1, len(index) + 1), index=index, name=ID_COLUMN_NAME)
    id_column = DataColumn.initialize_from_series(id_series)
    id_column.column_type = ColumnType.ID
    id_column.is_numeric = False
    data.add_column_first(id_column)
    return data


def descriptives_payload(case: dict) -> dict:
    # Drive the real recalculate_descriptive_study and read the supplements it attaches to its tables.
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.data.data_manager import DATA_MANAGER
    from src.side_area_panel.modules.descriptive.descriptive_main import recalculate_descriptive_study
    from src.side_area_panel.modules.descriptive.descriptive_result import DescriptiveResult, DescriptiveStudyConfig

    col = case["column"]
    cfg = DescriptiveStudyConfig(
        data_source="Auto",
        column_selector=[[col], []],
        show_normality=(case["mode"] == "normality"),
        normality_test=case.get("test"),
    )
    data = _build_data(case["data"]())
    original = DATA_MANAGER.get_data_from_data_label
    DATA_MANAGER.get_data_from_data_label = lambda *a, **k: data
    try:
        result = DescriptiveResult(unique_id=1, settings_panel_index=0, config=cfg)
        recalculate_descriptive_study(None, result, lambda _p: None)
    finally:
        DATA_MANAGER.get_data_from_data_label = original

    supplements = result.numeric_supplements()
    if case["mode"] == "summary":
        rows = next(s for s in supplements if s.get("kind") == "numeric_summary")["rows"]
        stats = next(r for r in rows if r["variable"] == col and r["group"] is None)
        return {"error": "", "stats": {key: _clean(stats[key]) for key in SUMMARY_KEYS}}
    rows = next(s for s in supplements if s.get("kind") == "normality")["rows"]
    row = next(r for r in rows if r["variable"] == col and r["group"] is None)
    return {"error": "", "statistic": _clean(row["norm_stat"]), "p": _clean(row["norm_p"])}


def run_case(case: dict, benchmarks: dict) -> BenchmarkCaseResult:
    actual = descriptives_payload(case)
    expected = benchmarks["studies"][case["study"]]
    comparisons = compare_payloads(
        actual,
        expected,
        tolerance=benchmarks.get("tolerance", 1e-8),
        relative_tolerance=RELATIVE_TOLERANCES.get(case["study"]),
    )
    return BenchmarkCaseResult(MODULE, case["study"], BENCHMARK_PATH, GENERATOR_PATH, comparisons)


def run_descriptives_benchmarks() -> list[BenchmarkCaseResult]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Missing descriptives R benchmark file: {BENCHMARK_PATH}\n"
            "Run: ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks"
        )
    benchmarks = load_json(BENCHMARK_PATH)
    return [run_case(case, benchmarks) for case in CASES]


def main() -> int:
    results = run_descriptives_benchmarks()
    report = render_report(results, HERE / "descriptives_benchmark_report.html")
    failed = [result for result in results if not result.passed]
    print(f"Descriptives benchmark report written to {report}")
    if failed:
        print(f"{len(failed)} descriptives benchmark study/studies failed.")
        return 1
    print("All descriptives benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
