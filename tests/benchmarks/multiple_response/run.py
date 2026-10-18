from __future__ import annotations

import math

from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report
from tests.benchmarks.multiple_response.cases import CASES
from tests.benchmarks.multiple_response.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE

MODULE = "multiple_response"
RELATIVE_TOLERANCES: dict = {}


def _clean(value):
    if value is None:
        return None
    value = float(value)
    return None if math.isnan(value) else value


def multiple_response_payload(case: dict) -> dict:
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.data.data import Data
    from src.data.data_manager import DATA_MANAGER
    from src.side_area_panel.modules.multiple_response.multiple_response_main import recalculate_multiple_response_study
    from src.side_area_panel.modules.multiple_response.multiple_response_result import (
        MultipleResponseResult,
        MultipleResponseStudyConfig,
    )

    cfg = MultipleResponseStudyConfig(
        data_source="Auto",
        column_selector=[list(case["columns"])],
        show_chart=False,
        interpretation=None,
    )
    data = Data.initialize_from_dataframe(case["data"]())
    original = DATA_MANAGER.get_data_from_data_label
    DATA_MANAGER.get_data_from_data_label = lambda *a, **k: data
    try:
        result = MultipleResponseResult(unique_id=1, settings_panel_index=0, config=cfg)
        recalculate_multiple_response_study(None, result, lambda _p: None)
    finally:
        DATA_MANAGER.get_data_from_data_label = original

    supplements = [s for s in result.numeric_supplements() if s.get("kind") == case["kind"]]
    if not supplements:
        raise AssertionError(f"{case['study']}: no supplement (error={result.error_message!r})")
    s = supplements[0]
    return {
        "error": "",
        "options": {
            opt: {
                "count": _clean(v["count"]),
                "pct_responses": _clean(v["pct_responses"]),
                "pct_cases": _clean(v["pct_cases"]),
            }
            for opt, v in s["options"].items()
        },
        "total_selections": _clean(s["total_selections"]),
        "n_cases": _clean(s["n_cases"]),
    }


def run_case(case: dict, benchmarks: dict) -> BenchmarkCaseResult:
    actual = multiple_response_payload(case)
    expected = benchmarks["studies"][case["study"]]
    comparisons = compare_payloads(
        actual,
        expected,
        tolerance=benchmarks.get("tolerance", 1e-8),
        relative_tolerance=RELATIVE_TOLERANCES.get(case["study"]),
    )
    return BenchmarkCaseResult(MODULE, case["study"], BENCHMARK_PATH, GENERATOR_PATH, comparisons)


def run_multiple_response_benchmarks() -> list[BenchmarkCaseResult]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Missing multiple-response R benchmark file: {BENCHMARK_PATH}\n"
            "Run: ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks"
        )
    benchmarks = load_json(BENCHMARK_PATH)
    return [run_case(case, benchmarks) for case in CASES]


def main() -> int:
    results = run_multiple_response_benchmarks()
    report = render_report(results, HERE / "multiple_response_benchmark_report.html")
    failed = [result for result in results if not result.passed]
    print(f"Multiple-response benchmark report written to {report}")
    if failed:
        print(f"{len(failed)} multiple-response benchmark study/studies failed.")
        return 1
    print("All multiple-response benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
