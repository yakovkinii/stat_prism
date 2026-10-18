from __future__ import annotations

import math

from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report
from tests.benchmarks.general_sem.cases import CASES, sem_data
from tests.benchmarks.general_sem.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE

MODULE = "general_sem"
# semopy vs lavaan: standardized estimates match closely; fit indices looser (chi-square scaling/SRMR).
RELATIVE_TOLERANCES = {"sem_fit": 1e-2, "sem_params": 1e-2}

STRUCTURE = [["v1", "v2", "v3"], ["v4", "v5", "v6"]]


def _clean(value):
    if value is None:
        return None
    value = float(value)
    return None if math.isnan(value) else value


def sem_payload(case: dict) -> dict:
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.data.data import Data
    from src.data.data_manager import DATA_MANAGER
    from src.side_area_panel.modules.general_sem.general_sem_main import recalculate_general_sem_study
    from src.side_area_panel.modules.general_sem.general_sem_result import GeneralSEMResult, GeneralSEMStudyConfig

    cfg = GeneralSEMStudyConfig(
        data_source="Auto",
        n_factors=2,
        column_selector=[list(group) for group in STRUCTURE],
        factor_names="F1,F2",
        paths=[{"from": "F1", "to": "F2", "type": "~"}],
        estimator="Maximum Likelihood (ML)",
        verbal_indicators=False,
        interpretation=None,
        plots=False,
    )
    data = Data.initialize_from_dataframe(sem_data())
    original = DATA_MANAGER.get_data_from_data_label
    DATA_MANAGER.get_data_from_data_label = lambda *a, **k: data
    try:
        result = GeneralSEMResult(unique_id=1, settings_panel_index=0, config=cfg)
        recalculate_general_sem_study(None, result, lambda _p: None)
    finally:
        DATA_MANAGER.get_data_from_data_label = original

    kind = case["kind"]
    supplements = [s for s in result.numeric_supplements() if s.get("kind") == kind]
    if not supplements:
        raise AssertionError(f"{case['study']}: no '{kind}' supplement (error={result.error_message!r})")
    s = supplements[0]

    if kind == "sem_fit":
        return {"error": "", **{k: _clean(s[k]) for k in ("chi2", "df", "p", "cfi", "tli", "rmsea")}}
    return {"error": "", "std": {key: _clean(val) for key, val in s["std"].items()}}


def run_case(case: dict, benchmarks: dict) -> BenchmarkCaseResult:
    actual = sem_payload(case)
    expected = benchmarks["studies"][case["study"]]
    comparisons = compare_payloads(
        actual,
        expected,
        tolerance=benchmarks.get("tolerance", 1e-8),
        relative_tolerance=RELATIVE_TOLERANCES.get(case["study"]),
    )
    return BenchmarkCaseResult(MODULE, case["study"], BENCHMARK_PATH, GENERATOR_PATH, comparisons)


def run_general_sem_benchmarks() -> list[BenchmarkCaseResult]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Missing general-SEM R benchmark file: {BENCHMARK_PATH}\n"
            "Run: ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks"
        )
    benchmarks = load_json(BENCHMARK_PATH)
    return [run_case(case, benchmarks) for case in CASES]


def main() -> int:
    results = run_general_sem_benchmarks()
    report = render_report(results, HERE / "general_sem_benchmark_report.html")
    failed = [result for result in results if not result.passed]
    print(f"General-SEM benchmark report written to {report}")
    if failed:
        print(f"{len(failed)} general-SEM benchmark study/studies failed.")
        return 1
    print("All general-SEM benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
