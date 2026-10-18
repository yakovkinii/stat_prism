from __future__ import annotations

import math

from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report
from tests.benchmarks.mean_comparison.cases import CASES
from tests.benchmarks.mean_comparison.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE

MODULE = "mean_comparison"
RELATIVE_TOLERANCES: dict = {}

_METHOD = {
    "homogeneous": "Parametric homogeneous (t-test/ANOVA)",
    "inhomogeneous": "Parametric inhomogeneous (Welch's)",
    "nonparametric": "Non-parametric (Mann-Whitney/Kruskal-Wallis)",
}
_ASSUMPTION = {"always": "Yes", "never": "No"}

# Fields carried from each supplement into the payload (must match the R generator's keys).
_FIELDS = {
    "ttest_homogeneous": ("t", "p", "df", "mean1", "sd1", "mean2", "sd2", "cohen_d", "ci_low", "ci_high"),
    "ttest_welch": ("t", "p", "df", "mean1", "sd1", "mean2", "sd2", "cohen_d", "ci_low", "ci_high"),
    "mann_whitney": ("u", "p", "rank_biserial", "median1", "iqr1", "median2", "iqr2"),
    "anova_oneway": ("f", "p", "df_between", "df_within", "eta2"),
    # partial_eta2 is pingouin's np2 -- no trusted R default reproduces it, so coefficient test only.
    "anova_welch": ("f", "p", "df_between", "df_within"),
    "kruskal": ("h", "p", "df"),
}
_POSTHOC_KINDS = {"posthoc_tukey", "posthoc_tamhane", "posthoc_dunn"}


def _clean(value):
    value = float(value)
    return None if math.isnan(value) else value


def mean_comparison_payload(case: dict) -> dict:
    # Drive the real recalculate_mean_comparison_study and read the supplement its table attached.
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.data.data import Data
    from src.data.data_manager import DATA_MANAGER
    from src.side_area_panel.modules.mean_comparison.mean_comparison_main import recalculate_mean_comparison_study
    from src.side_area_panel.modules.mean_comparison.mean_comparison_result import (
        MeanComparisonResult,
        MeanComparisonStudyConfig,
    )

    cfg = MeanComparisonStudyConfig(
        data_source="Auto",
        column_selector=[["y"], ["g"]],
        method=_METHOD[case["method"]],
        grouping_missing="Skip missing",
        assumption_checks=_ASSUMPTION[case["assumption"]],
        effect_size=True,
        verbal_indicators=False,
        interpretation=None,
        confidence_intervals=True,
        number_columns=False,
        plots=False,
    )
    data = Data.initialize_from_dataframe(case["data"]())
    original = DATA_MANAGER.get_data_from_data_label
    DATA_MANAGER.get_data_from_data_label = lambda *a, **k: data
    try:
        result = MeanComparisonResult(unique_id=1, settings_panel_index=0, config=cfg)
        recalculate_mean_comparison_study(None, result, lambda _p: None)
    finally:
        DATA_MANAGER.get_data_from_data_label = original

    kind = case["kind"]
    supplements = [s for s in result.numeric_supplements() if s.get("kind") == kind]
    if not supplements:
        raise AssertionError(f"{case['study']}: no '{kind}' supplement (error={result.error_message!r})")

    if kind in _POSTHOC_KINDS:
        return {"error": "", "pairs": {pair: _clean(p) for pair, p in supplements[0]["pairs"].items()}}

    rows = supplements[0]["rows"]
    if kind == "normality_check":
        groups = {row["group"]: {"w": _clean(row["w"]), "p": _clean(row["p"])} for row in rows}
        return {"error": "", "groups": groups}
    if kind == "homogeneity_check":
        row = next(r for r in rows if r["variable"] == "y")
        return {"error": "", "f": _clean(row["f"]), "p": _clean(row["p"])}

    row = next(r for r in rows if r["variable"] == "y")
    return {"error": "", **{field: _clean(row[field]) for field in _FIELDS[kind]}}


def run_case(case: dict, benchmarks: dict) -> BenchmarkCaseResult:
    actual = mean_comparison_payload(case)
    expected = benchmarks["studies"][case["study"]]
    comparisons = compare_payloads(
        actual,
        expected,
        tolerance=benchmarks.get("tolerance", 1e-8),
        relative_tolerance=RELATIVE_TOLERANCES.get(case["study"]),
    )
    return BenchmarkCaseResult(MODULE, case["study"], BENCHMARK_PATH, GENERATOR_PATH, comparisons)


def run_mean_comparison_benchmarks() -> list[BenchmarkCaseResult]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Missing mean-comparison R benchmark file: {BENCHMARK_PATH}\n"
            "Run: ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks"
        )
    benchmarks = load_json(BENCHMARK_PATH)
    return [run_case(case, benchmarks) for case in CASES]


def main() -> int:
    results = run_mean_comparison_benchmarks()
    report = render_report(results, HERE / "mean_comparison_benchmark_report.html")
    failed = [result for result in results if not result.passed]
    print(f"Mean-comparison benchmark report written to {report}")
    if failed:
        print(f"{len(failed)} mean-comparison benchmark study/studies failed.")
        return 1
    print("All mean-comparison benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
