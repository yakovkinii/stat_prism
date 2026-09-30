from __future__ import annotations

import math

from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report
from tests.benchmarks.reliability.cases import CASES
from tests.benchmarks.reliability.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE


MODULE = "reliability"
RELATIVE_TOLERANCES = {
    "tetrachoric_binary_items_no_omega": 1e-4,
    "polychoric_likert_items_no_omega": 1e-4,
}


def _clean_number(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def reliability_numeric_payload(numeric) -> dict:
    return {
        "error": numeric.error,
        "scale": {
            "n_items": numeric.n_items,
            "alpha": _clean_number(numeric.alpha),
            "omega": _clean_number(numeric.omega),
        },
        "items": [
            {
                "name": item.name,
                "item_rest": _clean_number(item.item_rest),
                "alpha_deleted": _clean_number(item.alpha_deleted),
                "omega_deleted": _clean_number(item.omega_deleted),
            }
            for item in numeric.items
        ],
    }


def run_case(case: dict, benchmarks: dict) -> BenchmarkCaseResult:
    from src.side_area_panel.modules.reliability.reliability_main import compute_reliability
    from src.common.constant import ColumnType
    from src.data.data import Data

    study = case["study"]
    config = case["config"]()
    df = case["data"]()
    items = config.column_selector[0]
    if case.get("ordinal_order"):
        data = Data.initialize_from_dataframe(df)
        for column_name, order in case["ordinal_order"].items():
            data[column_name].column_type = ColumnType.ORDINAL
            data[column_name].is_numeric = False
            data[column_name].order = {value: index for index, value in enumerate(order, start=1)}
        item_frame = data.get_dataframe(columns=items, map_ordinal=True)
    else:
        item_frame = df[items].copy()
    numeric = compute_reliability(config, item_frame)
    actual = reliability_numeric_payload(numeric)
    expected = benchmarks["studies"][study]
    comparisons = compare_payloads(
        actual,
        expected,
        tolerance=benchmarks.get("tolerance", 1e-8),
        relative_tolerance=RELATIVE_TOLERANCES.get(study),
    )
    return BenchmarkCaseResult(MODULE, study, BENCHMARK_PATH, GENERATOR_PATH, comparisons)


def run_reliability_benchmarks() -> list[BenchmarkCaseResult]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Missing reliability R benchmark file: {BENCHMARK_PATH}\n"
            "Run: ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks"
        )
    benchmarks = load_json(BENCHMARK_PATH)
    return [run_case(case, benchmarks) for case in CASES]


def main() -> int:
    results = run_reliability_benchmarks()
    report = render_report(results, HERE / "reliability_benchmark_report.html")
    failed = [result for result in results if not result.passed]
    print(f"Reliability benchmark report written to {report}")
    if failed:
        print(f"{len(failed)} reliability benchmark study/studies failed.")
        return 1
    print("All reliability benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
