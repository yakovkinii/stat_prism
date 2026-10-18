from __future__ import annotations

import math

from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report
from tests.benchmarks.power_analysis.cases import CASES
from tests.benchmarks.power_analysis.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE

MODULE = "power_analysis"
# StatPrism's correlation power follows Cohen's (1988) method as pwr.r.test does. The sample-size
# solves round to a whole n and match exactly; the effect-size / power solves differ only at the
# iterative-root-finder tolerance (statsmodels/brentq vs pwr's uniroot), so they get a small slack.
RELATIVE_TOLERANCES = {
    "two_sample_effect": 1e-3,
    "paired_effect": 1e-3,
    "anova_effect": 1e-3,
    "corr_power": 1e-3,
    "corr_effect": 1e-3,
}


def _clean(value):
    if value is None:
        return None
    value = float(value)
    return None if math.isnan(value) else value


def power_analysis_payload(case: dict) -> dict:
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.side_area_panel.modules.power_analysis.power_analysis_main import recalculate_power_analysis_study
    from src.side_area_panel.modules.power_analysis.power_analysis_result import (
        PowerAnalysisResult,
        PowerAnalysisStudyConfig,
    )

    cfg = PowerAnalysisStudyConfig(
        test_type=case["test"],
        solve_for=case["solve_for"],
        alpha=case.get("alpha", "0.05"),
        power=case.get("power", "0.80"),
        effect_size=case.get("effect_size", "0.5"),
        sample_size=case.get("sample_size", "30"),
        n_groups=case.get("n_groups", "3"),
        tails=case.get("tails", "Two-sided"),
    )
    # Power analysis takes no data source -- it solves closed-form relationships.
    result = PowerAnalysisResult(unique_id=1, settings_panel_index=0, config=cfg)
    recalculate_power_analysis_study(None, result, lambda _p: None)

    supplements = [s for s in result.numeric_supplements() if s.get("kind") == "power_analysis"]
    if not supplements:
        raise AssertionError(f"{case['study']}: no supplement (error={result.error_message!r})")
    s = supplements[0]
    return {"error": "", **{field: _clean(s[field]) for field in case["fields"]}}


def run_case(case: dict, benchmarks: dict) -> BenchmarkCaseResult:
    actual = power_analysis_payload(case)
    expected = benchmarks["studies"][case["study"]]
    comparisons = compare_payloads(
        actual,
        expected,
        tolerance=benchmarks.get("tolerance", 1e-8),
        relative_tolerance=RELATIVE_TOLERANCES.get(case["study"]),
    )
    return BenchmarkCaseResult(MODULE, case["study"], BENCHMARK_PATH, GENERATOR_PATH, comparisons)


def run_power_analysis_benchmarks() -> list[BenchmarkCaseResult]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Missing power-analysis R benchmark file: {BENCHMARK_PATH}\n"
            "Run: ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks"
        )
    benchmarks = load_json(BENCHMARK_PATH)
    return [run_case(case, benchmarks) for case in CASES]


def main() -> int:
    results = run_power_analysis_benchmarks()
    report = render_report(results, HERE / "power_analysis_benchmark_report.html")
    failed = [result for result in results if not result.passed]
    print(f"Power-analysis benchmark report written to {report}")
    if failed:
        print(f"{len(failed)} power-analysis benchmark study/studies failed.")
        return 1
    print("All power-analysis benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
