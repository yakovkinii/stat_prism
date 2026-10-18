from __future__ import annotations

import math

from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report
from tests.benchmarks.confirmatory_factor_analysis.cases import CASES
from tests.benchmarks.confirmatory_factor_analysis.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE

MODULE = "confirmatory_factor_analysis"
# ML semopy vs lavaan: standardized loadings / factor correlation are close; fit indices looser
# (chi-square scaling, SRMR flavor). DWLS is looser still: semopy fits the standardized codes, not
# polychoric correlations, so it is not expected to match lavaan WLSMV exactly -- flagged.
RELATIVE_TOLERANCES = {
    "cfa_fit": 1e-2,
    "cfa_loadings": 5e-3,
    "cfa_phi": 5e-3,
    "cfa_dwls_fit": 5e-2,
    "cfa_dwls_loadings": 5e-2,
    "cfa_dwls_phi": 5e-2,
    # ULS loadings depend on the polychoric matrix, which differs slightly between StatPrism's in-house
    # routine and lavaan's -> a little looser.
    "cfa_uls_loadings": 2e-2,
    "cfa_uls_phi": 2e-2,
    "cfa_orthogonal_loadings": 5e-3,
    "cfa_second_order": 1e-2,
    "cfa_cross_loading_loadings": 5e-3,
    "cfa_residual_fit": 2e-2,
}

STRUCTURE = [["v1", "v2", "v3"], ["v4", "v5", "v6"]]


def _clean(value):
    if value is None:
        return None
    value = float(value)
    return None if math.isnan(value) else value


def cfa_payload(case: dict) -> dict:
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.data.data import Data
    from src.data.data_manager import DATA_MANAGER
    from src.side_area_panel.modules.confirmatory_factor_analysis.confirmatory_factor_analysis_main import (
        recalculate_cfa_study,
    )
    from src.side_area_panel.modules.confirmatory_factor_analysis.confirmatory_factor_analysis_result import (
        CFAResult,
        CFAStudyConfig,
    )

    structure = case.get("structure", STRUCTURE)
    cfg = CFAStudyConfig(
        data_source="Auto",
        column_selector=[list(group) for group in structure],
        n_factors=len(structure),
        estimator=case["estimator"],
        allow_factor_correlation=case.get("allow_factor_correlation", True),
        second_order=case.get("second_order", False),
        modification_hints=False,
        correlated_residuals=False,
        cross_loadings=case.get("cross_loadings", []),
        residual_correlations=case.get("residual_correlations", []),
        verbal_indicators=False,
        interpretation=None,
        number_columns=False,
        plots=False,
    )
    data = Data.initialize_from_dataframe(case["data"]())
    original = DATA_MANAGER.get_data_from_data_label
    DATA_MANAGER.get_data_from_data_label = lambda *a, **k: data
    try:
        result = CFAResult(unique_id=1, settings_panel_index=0, config=cfg)
        recalculate_cfa_study(None, result, lambda _p: None)
    finally:
        DATA_MANAGER.get_data_from_data_label = original

    kind = case["kind"]
    supplements = [s for s in result.numeric_supplements() if s.get("kind") == kind]
    if not supplements:
        raise AssertionError(f"{case['study']}: no '{kind}' supplement (error={result.error_message!r})")
    s = supplements[0]

    if kind == "cfa_fit":
        return {"error": "", **{k: _clean(s[k]) for k in ("chi2", "df", "p", "rmsea", "cfi", "tli", "srmr")}}
    if kind == "cfa_loadings":
        return {"error": "", "std_loadings": [[_clean(v) for v in row] for row in s["std_loadings"]]}
    if kind == "cfa_second_order":
        return {"error": "", "loadings": {k: _clean(v) for k, v in s["loadings"].items()}}
    return {"error": "", "phi": [[_clean(v) for v in row] for row in s["phi"]]}


def run_case(case: dict, benchmarks: dict) -> BenchmarkCaseResult:
    actual = cfa_payload(case)
    expected = benchmarks["studies"][case["study"]]
    comparisons = compare_payloads(
        actual,
        expected,
        tolerance=benchmarks.get("tolerance", 1e-8),
        relative_tolerance=RELATIVE_TOLERANCES.get(case["study"]),
    )
    return BenchmarkCaseResult(MODULE, case["study"], BENCHMARK_PATH, GENERATOR_PATH, comparisons)


def run_confirmatory_factor_analysis_benchmarks() -> list[BenchmarkCaseResult]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Missing CFA R benchmark file: {BENCHMARK_PATH}\n"
            "Run: ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks"
        )
    benchmarks = load_json(BENCHMARK_PATH)
    return [run_case(case, benchmarks) for case in CASES]


def main() -> int:
    results = run_confirmatory_factor_analysis_benchmarks()
    report = render_report(results, HERE / "confirmatory_factor_analysis_benchmark_report.html")
    failed = [result for result in results if not result.passed]
    print(f"CFA benchmark report written to {report}")
    if failed:
        print(f"{len(failed)} CFA benchmark study/studies failed.")
        return 1
    print("All CFA benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
