from __future__ import annotations

import math

from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report
from tests.benchmarks.exploratory_factor_analysis.cases import CASES, efa_data
from tests.benchmarks.exploratory_factor_analysis.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE

MODULE = "exploratory_factor_analysis"
# Unrotated MINRES/ML loadings match psych closely. Rotated loadings, oblique phi/structure, PAF and
# the polychoric path depend on rotation-normalization and polychoric conventions that differ between
# factor_analyzer and psych, so they use loose, clearly-flagged tolerances (they may still fail -- the
# point is that every supported branch has a test against R).
RELATIVE_TOLERANCES = {
    "loadings_unrotated": 1e-3,
    "loadings_ml": 1e-3,
    "loadings_principal": 1e-2,
    "loadings_varimax": 5e-2,
    "loadings_quartimax": 5e-2,
    "loadings_equamax": 5e-2,
    "loadings_promax": 5e-2,
    "loadings_oblimin": 5e-2,
    "loadings_quartimin": 5e-2,
    "phi_promax": 1e-1,
    "phi_oblimin": 1e-1,
    "structure_promax": 1e-1,
    "structure_oblimin": 1e-1,
    "diagnostics_poly": 2e-2,
    "eigenvalues_poly": 2e-2,
    "loadings_poly": 5e-2,
}
# Rotated loadings / structure can differ by rotation-convergence noise on the near-ZERO cross-loadings
# (the varimax/oblimin criterion is flat there), where a relative tolerance is meaningless. An absolute
# tolerance lets those tiny entries match while the substantive loadings still agree closely.
ABSOLUTE_TOLERANCES = {
    "loadings_varimax": 0.02,
    "loadings_quartimax": 0.02,
    "loadings_equamax": 0.02,
    "loadings_promax": 0.02,
    "loadings_oblimin": 0.02,
    "loadings_quartimin": 0.02,
    "structure_promax": 0.02,
    "structure_oblimin": 0.02,
}


def _clean(value):
    if value is None:
        return None
    value = float(value)
    return None if math.isnan(value) else value


def _align(loadings):
    # Canonicalise the unidentified sign and factor order: flip each column so its largest-magnitude
    # entry is positive, then order columns by descending sum of squares. Applied identically in R.
    import numpy as np

    mat = np.array(loadings, dtype=float)
    for j in range(mat.shape[1]):
        col = mat[:, j]
        if col[int(np.argmax(np.abs(col)))] < 0:
            mat[:, j] = -col
    order = np.argsort(-(mat**2).sum(axis=0))
    return mat[:, order].tolist()


def efa_payload(case: dict) -> dict:
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.data.data import Data
    from src.data.data_manager import DATA_MANAGER
    from src.side_area_panel.modules.exploratory_factor_analysis.exploratory_factor_analysis_main import (
        recalculate_factor_analysis_study,
    )
    from src.side_area_panel.modules.exploratory_factor_analysis.exploratory_factor_analysis_result import (
        FactorAnalysisResult,
        FactorAnalysisStudyConfig,
    )

    cfg = FactorAnalysisStudyConfig(
        data_source="Auto",
        column_selector=[["v1", "v2", "v3", "v4", "v5", "v6"]],
        correlation_method=case.get("correlation_method", "Pearson"),
        method=case.get("method", "Minimum Residual (MINRES)"),
        rotation=case.get("rotation", "none"),
        n_factors=2,
        factor_names=None,
        kaiser_normalization=False,
        verbal_indicators=False,
        show_item_msa=True,
        show_eigenvalues=True,
        sort_by_factor_loadings=False,
        plots=False,
        number_columns=False,
        interpretation=None,
    )
    data = Data.initialize_from_dataframe(case.get("data", efa_data)())
    original = DATA_MANAGER.get_data_from_data_label
    DATA_MANAGER.get_data_from_data_label = lambda *a, **k: data
    try:
        result = FactorAnalysisResult(unique_id=1, settings_panel_index=0, config=cfg)
        recalculate_factor_analysis_study(None, result, lambda _p: None)
    finally:
        DATA_MANAGER.get_data_from_data_label = original

    kind = case["kind"]
    supplements = [s for s in result.numeric_supplements() if s.get("kind") == kind]
    if not supplements:
        raise AssertionError(f"{case['study']}: no '{kind}' supplement (error={result.error_message!r})")
    s = supplements[0]

    if kind == "efa_diagnostics":
        return {
            "error": "",
            "kmo": _clean(s["kmo"]),
            "msa": {k: _clean(v) for k, v in s["msa"].items()},
            "bartlett_chi2": _clean(s["bartlett_chi2"]),
            "bartlett_df": _clean(s["bartlett_df"]),
            "bartlett_p": _clean(s["bartlett_p"]),
        }
    if kind == "efa_eigenvalues":
        return {
            "error": "",
            "eigenvalues": [_clean(v) for v in s["eigenvalues"]],
            "variance_pct": [_clean(v) for v in s["variance_pct"]],
            "cumulative_pct": [_clean(v) for v in s["cumulative_pct"]],
            "n_kaiser": _clean(s["n_kaiser"]),
        }
    if kind == "efa_phi":
        return {"error": "", "phi": [[_clean(v) for v in row] for row in s["phi"]]}
    if kind == "efa_structure":
        return {"error": "", "structure": [[_clean(v) for v in row] for row in _align(s["structure"])]}
    # efa_loadings
    return {
        "error": "",
        "loadings": [[_clean(v) for v in row] for row in _align(s["loadings"])],
        "communalities": [_clean(v) for v in s["communalities"]],
        "uniquenesses": [_clean(v) for v in s["uniquenesses"]],
    }


def run_case(case: dict, benchmarks: dict) -> BenchmarkCaseResult:
    actual = efa_payload(case)
    expected = benchmarks["studies"][case["study"]]
    comparisons = compare_payloads(
        actual,
        expected,
        tolerance=ABSOLUTE_TOLERANCES.get(case["study"], benchmarks.get("tolerance", 1e-8)),
        relative_tolerance=RELATIVE_TOLERANCES.get(case["study"]),
    )
    return BenchmarkCaseResult(MODULE, case["study"], BENCHMARK_PATH, GENERATOR_PATH, comparisons)


def run_exploratory_factor_analysis_benchmarks() -> list[BenchmarkCaseResult]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Missing EFA R benchmark file: {BENCHMARK_PATH}\n"
            "Run: ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks"
        )
    benchmarks = load_json(BENCHMARK_PATH)
    return [run_case(case, benchmarks) for case in CASES]


def main() -> int:
    results = run_exploratory_factor_analysis_benchmarks()
    report = render_report(results, HERE / "exploratory_factor_analysis_benchmark_report.html")
    failed = [result for result in results if not result.passed]
    print(f"EFA benchmark report written to {report}")
    if failed:
        print(f"{len(failed)} EFA benchmark study/studies failed.")
        return 1
    print("All EFA benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
