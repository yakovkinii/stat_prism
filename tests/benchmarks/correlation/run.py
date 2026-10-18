from __future__ import annotations

import math

from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report
from tests.benchmarks.correlation.cases import CASES
from tests.benchmarks.correlation.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE

MODULE = "correlation"
# Tetrachoric / polychoric rho are iterative latent MLEs compared against polycor / psych (raw, no
# smoothing); they agree to ~1e-5 except near |rho|=1 where the likelihood is flat.
RELATIVE_TOLERANCES = {
    "tetrachoric_square": 1e-3,
    "polychoric_square": 1e-3,
    "tetrachoric_cross": 1e-3,
    "polychoric_cross": 1e-3,
}

# Studies whose p-value StatPrism computes with a method that a trusted R package reproduces, so p is
# validated. Tetrachoric uses a likelihood-ratio test of rho = 0 which (thresholds fixed at the
# marginals) equals the G^2 independence test -> DescTools::GTest. Excluded (coefficient only):
# polychoric -- its LR test does not reduce to the G^2 independence test (an r x c table has more
# than one degree of freedom), and no package exposes the latent-model LR p.
VALIDATE_P = {
    "pearson_square",
    "spearman_square",
    "kendall_square",
    "kendall_tau_c_square",
    "phi_square",
    "tetrachoric_square",
    "pearson_cross",
    "pearson_partial",
    "spearman_partial",
    "spearman_partial_cross",
    "pearson_partial_cross",
    "spearman_cross",
    "kendall_cross",
    "kendall_tau_c_cross",
    "phi_cross",
    "tetrachoric_cross",
}


def _clean(value):
    value = float(value)
    return None if math.isnan(value) else value


def _pair_entry(study, r, p):
    entry = {"r": _clean(r)}
    if study in VALIDATE_P:
        entry["p"] = _clean(p)
    return entry


def _square_pairs(study, corr, pmat, columns) -> dict:
    pairs = {}
    for i, row in enumerate(columns):
        for j, col in enumerate(columns):
            if i <= j:
                continue
            pairs[f"{row}__{col}"] = _pair_entry(study, corr.loc[row, col], pmat.loc[row, col])
    return pairs


def _cross_pairs(study, corr, pmat, rows, cols) -> dict:
    pairs = {}
    for row in rows:
        for col in cols:
            pairs[f"{row}__{col}"] = _pair_entry(study, corr.loc[row, col], pmat.loc[row, col])
    return pairs


def _column_selector(case: dict):
    mode = case["mode"]
    if mode == "square":
        return [list(case["columns"]), [], []]
    if mode == "partial":
        return [list(case["columns"]), list(case["controls"]), []]
    if mode == "cross":
        return [list(case["rows"]), [], list(case["cols"])]
    if mode == "partial_cross":
        return [list(case["rows"]), list(case["controls"]), list(case["cols"])]
    raise ValueError(f"Unknown case mode: {mode}")


def correlation_payload(case: dict) -> dict:
    # Drive the real recalculate_correlation_study and read the numeric supplement it attaches to the
    # result table -- the same path the GUI runs. (registry first so the BaseResult <-> *Result
    # mutual import resolves before correlation_result is pulled.)
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.data.data import Data
    from src.data.data_manager import DATA_MANAGER
    from src.side_area_panel.modules.correlation.correlation_main import recalculate_correlation_study
    from src.side_area_panel.modules.correlation.correlation_result import CorrelationResult, CorrelationStudyConfig

    cfg = CorrelationStudyConfig(
        data_source="Auto",
        column_selector=_column_selector(case),
        correlation_type=case["correlation_type"],
    )
    data = Data.initialize_from_dataframe(case["data"]())
    original = DATA_MANAGER.get_data_from_data_label
    DATA_MANAGER.get_data_from_data_label = lambda *a, **k: data
    try:
        result = CorrelationResult(unique_id=1, settings_panel_index=0, config=cfg)
        recalculate_correlation_study(None, result, lambda _p: None)
    finally:
        DATA_MANAGER.get_data_from_data_label = original

    supplements = [s for s in result.numeric_supplements() if s.get("kind") == "correlation"]
    if not supplements:
        raise AssertionError(f"{case['study']}: no correlation supplement (error={result.error_message!r})")
    corr = supplements[0]["correlation_matrix"]
    pmat = supplements[0]["p_matrix"]
    study = case["study"]

    if case["mode"] in ("square", "partial"):
        pairs = _square_pairs(study, corr, pmat, list(corr.index))
    else:
        pairs = _cross_pairs(study, corr, pmat, list(corr.index), list(corr.columns))
    return {"error": "", "pairs": pairs}


def run_case(case: dict, benchmarks: dict) -> BenchmarkCaseResult:
    actual = correlation_payload(case)
    expected = benchmarks["studies"][case["study"]]
    comparisons = compare_payloads(
        actual,
        expected,
        tolerance=benchmarks.get("tolerance", 1e-8),
        relative_tolerance=RELATIVE_TOLERANCES.get(case["study"]),
    )
    return BenchmarkCaseResult(MODULE, case["study"], BENCHMARK_PATH, GENERATOR_PATH, comparisons)


def run_correlation_benchmarks() -> list[BenchmarkCaseResult]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Missing correlation R benchmark file: {BENCHMARK_PATH}\n"
            "Run: ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks"
        )
    benchmarks = load_json(BENCHMARK_PATH)
    return [run_case(case, benchmarks) for case in CASES]


def main() -> int:
    results = run_correlation_benchmarks()
    report = render_report(results, HERE / "correlation_benchmark_report.html")
    failed = [result for result in results if not result.passed]
    print(f"Correlation benchmark report written to {report}")
    if failed:
        print(f"{len(failed)} correlation benchmark study/studies failed.")
        return 1
    print("All correlation benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
