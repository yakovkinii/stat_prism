from __future__ import annotations

import math

from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report
from tests.benchmarks.contingency.cases import CASES
from tests.benchmarks.contingency.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE

MODULE = "contingency"
RELATIVE_TOLERANCES: dict = {}


def _clean(value):
    if value is None:
        return None
    value = float(value)
    return None if math.isnan(value) else value


def _nested(mapping):
    return {str(outer): {str(inner): _clean(v) for inner, v in row.items()} for outer, row in mapping.items()}


def contingency_payload(case: dict) -> dict:
    # Drive the real recalculate_contingency_study and read the supplement its table attached.
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.data.data import Data
    from src.data.data_manager import DATA_MANAGER
    from src.side_area_panel.modules.contingency.contingency_main import recalculate_contingency_study
    from src.side_area_panel.modules.contingency.contingency_result import (
        ContingencyResult,
        ContingencyStudyConfig,
    )

    cfg = ContingencyStudyConfig(
        data_source="Auto",
        column_selector=[["v1"], ["v2"]],
        continuity_correction=bool(case.get("correction", False)),
        effect_size=True,
        percentages=case.get("percentages", "None"),
        post_hoc=bool(case.get("post_hoc", False)),
        verbal_indicators=False,
        interpretation=case.get("interpretation", None),
        mcnemar=bool(case.get("mcnemar", False)),
        plots=False,
    )
    data = Data.initialize_from_dataframe(case["data"]())
    original = DATA_MANAGER.get_data_from_data_label
    DATA_MANAGER.get_data_from_data_label = lambda *a, **k: data
    try:
        result = ContingencyResult(unique_id=1, settings_panel_index=0, config=cfg)
        recalculate_contingency_study(None, result, lambda _p: None)
    finally:
        DATA_MANAGER.get_data_from_data_label = original

    kind = case["kind"]
    supplements = [s for s in result.numeric_supplements() if s.get("kind") == kind]
    if not supplements:
        raise AssertionError(f"{case['study']}: no '{kind}' supplement (error={result.error_message!r})")
    s = supplements[0]

    if kind == "contingency_counts":
        return {
            "error": "",
            "counts": _nested(s["counts"]),
            "row_totals": {str(k): _clean(v) for k, v in s["row_totals"].items()},
            "col_totals": {str(k): _clean(v) for k, v in s["col_totals"].items()},
            "grand_total": _clean(s["grand_total"]),
        }
    if kind == "contingency_percent":
        return {
            "error": "",
            "mode": s["mode"],
            "inner": _nested(s["inner"]),
            "right_margin": {str(k): _clean(v) for k, v in s["right_margin"].items()},
            "bottom_margin": {str(k): _clean(v) for k, v in s["bottom_margin"].items()},
        }
    if kind == "contingency_residuals":
        return {"error": "", "residuals": _nested(s["residuals"])}
    if kind == "contingency_mcnemar":
        return {"error": "", "stat": _clean(s["stat"]), "df": _clean(s["df"]), "p": _clean(s["p"])}

    # contingency_chi2: include Fisher fields only when the module computed them (2x2 + low expected).
    payload = {
        "error": "",
        "chi2": _clean(s["chi2"]),
        "n": _clean(s["n"]),
        "dof": _clean(s["dof"]),
        "p": _clean(s["p"]),
        "cramer_v": _clean(s["cramer_v"]),
    }
    if "fisher_odds" in s:
        payload["fisher_odds"] = _clean(s["fisher_odds"])
        payload["fisher_p"] = _clean(s["fisher_p"])
    return payload


def run_case(case: dict, benchmarks: dict) -> BenchmarkCaseResult:
    actual = contingency_payload(case)
    expected = benchmarks["studies"][case["study"]]
    comparisons = compare_payloads(
        actual,
        expected,
        tolerance=benchmarks.get("tolerance", 1e-8),
        relative_tolerance=RELATIVE_TOLERANCES.get(case["study"]),
    )
    return BenchmarkCaseResult(MODULE, case["study"], BENCHMARK_PATH, GENERATOR_PATH, comparisons)


def run_contingency_benchmarks() -> list[BenchmarkCaseResult]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Missing contingency R benchmark file: {BENCHMARK_PATH}\n"
            "Run: ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks"
        )
    benchmarks = load_json(BENCHMARK_PATH)
    return [run_case(case, benchmarks) for case in CASES]


def main() -> int:
    results = run_contingency_benchmarks()
    report = render_report(results, HERE / "contingency_benchmark_report.html")
    failed = [result for result in results if not result.passed]
    print(f"Contingency benchmark report written to {report}")
    if failed:
        print(f"{len(failed)} contingency benchmark study/studies failed.")
        return 1
    print("All contingency benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
