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


def descriptives_payload(case: dict) -> dict:
    # Load registry first so the BaseResult <-> *Result mutual import resolves before descriptive_main
    # pulls descriptive_result (otherwise ImportError on a cold import).
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.data.data import Data
    from src.side_area_panel.modules.descriptive.descriptive_main import _normality_stats, _numeric_stats

    df = case["data"]()
    col = case["column"]
    data = Data.initialize_from_dataframe(df)

    if case["mode"] == "summary":
        stats = _numeric_stats(data, col, None, df[col])
        return {"error": "", "stats": {key: _clean(stats[key]) for key in SUMMARY_KEYS}}
    if case["mode"] == "normality":
        result = _normality_stats(col, None, df[col], case["test"])
        return {"error": "", "statistic": _clean(result["norm_stat"]), "p": _clean(result["norm_p"])}
    raise ValueError(f"Unknown case mode: {case['mode']}")


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
