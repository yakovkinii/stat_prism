from __future__ import annotations

import math

from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report
from tests.benchmarks.correlation.cases import CASES
from tests.benchmarks.correlation.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE

MODULE = "correlation"
# Tetrachoric / polychoric are iterative latent-correlation MLEs compared raw (psych smooth=FALSE).
# They agree to ~1e-5 except where the likelihood is flat near |rho|=1 (e.g. a zero-cell 2x2 table),
# so allow a small relative gap on those near-boundary estimates.
RELATIVE_TOLERANCES = {
    "tetrachoric_square": 1e-3,
    "polychoric_square": 1e-3,
}


def _clean_number(value):
    value = float(value)
    if math.isnan(value):
        return None
    return value


def _square_pairs(matrix, columns) -> dict:
    """Lower-triangle pairs in the same layout calculate_correlations fills (row index > col index),
    keyed '<row>__<col>'."""
    pairs = {}
    for i, row in enumerate(columns):
        for j, col in enumerate(columns):
            if i <= j:
                continue
            pairs[f"{row}__{col}"] = _clean_number(matrix.loc[row, col])
    return pairs


def _cross_pairs(matrix, rows, cols) -> dict:
    pairs = {}
    for row in rows:
        for col in cols:
            pairs[f"{row}__{col}"] = _clean_number(matrix.loc[row, col])
    return pairs


def correlation_payload(case: dict) -> dict:
    # Imported lazily so the Qt-touching import graph is only pulled in when a case actually runs.
    # Load registry first: it resolves the mutual import between BaseResult and the per-module
    # *Result classes. Importing the correlation math module first would pull correlation_result
    # mid-initialisation (registry re-imports CorrelationResult from it) and raise ImportError.
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.side_area_panel.modules.common.mathematics.correlation.correlation import (
        calculate_correlations,
        calculate_cross_correlations,
        calculate_partial_correlations,
        calculate_partial_cross_correlations,
    )
    from src.side_area_panel.modules.correlation.correlation_result import CORRELATION_TYPE_MAP

    df = case["data"]()
    kind = CORRELATION_TYPE_MAP[case["correlation_type"]]
    mode = case["mode"]

    if mode == "square":
        columns = case["columns"]
        matrix, _p, _df = calculate_correlations(df[columns], kind)
        pairs = _square_pairs(matrix, columns)
    elif mode == "partial":
        columns, controls = case["columns"], case["controls"]
        matrix, _p, _df = calculate_partial_correlations(df[columns + controls], columns, controls, kind)
        pairs = _square_pairs(matrix, columns)
    elif mode == "cross":
        rows, cols = case["rows"], case["cols"]
        matrix, _p, _df = calculate_cross_correlations(df[rows + cols], rows, cols, kind)
        pairs = _cross_pairs(matrix, rows, cols)
    elif mode == "partial_cross":
        rows, cols, controls = case["rows"], case["cols"], case["controls"]
        matrix, _p, _df = calculate_partial_cross_correlations(df[rows + cols + controls], rows, cols, controls, kind)
        pairs = _cross_pairs(matrix, rows, cols)
    else:
        raise ValueError(f"Unknown case mode: {mode}")

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
