from __future__ import annotations

import math

from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report
from tests.benchmarks.paired.cases import CASES
from tests.benchmarks.paired.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE

MODULE = "paired"
RELATIVE_TOLERANCES: dict = {}

_METHOD = {
    "parametric": "Parametric (paired t / RM-ANOVA)",
    "nonparametric": "Non-parametric (Wilcoxon / Friedman)",
}
_ASSUMPTION = {"always": "Yes", "never": "No"}

# Fields carried from each single-row supplement into the payload (must match the R generator keys).
_FIELDS = {
    "paired_t": ("t", "p", "df", "cohen_dz"),
    "wilcoxon": ("w", "p", "rbc"),
    "rm_anova": ("f", "df1", "df2", "p", "ng2", "p_gg", "eps"),
    "friedman": ("chi2", "df", "p", "kendall_w"),
}
_POSTHOC_KINDS = {"paired_posthoc_param", "paired_posthoc_nonparam"}


def _clean(value):
    if value is None:
        return None
    value = float(value)
    return None if math.isnan(value) else value


def paired_payload(case: dict) -> dict:
    # Drive the real recalculate_paired_study and read the supplement its tables attached.
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.data.data import Data
    from src.data.data_manager import DATA_MANAGER
    from src.side_area_panel.modules.paired.paired_main import recalculate_paired_study
    from src.side_area_panel.modules.paired.paired_result import PairedResult, PairedStudyConfig

    cfg = PairedStudyConfig(
        data_source="Auto",
        column_selector=[list(case["conditions"])],
        method=_METHOD[case["method"]],
        assumption_checks=_ASSUMPTION[case["assumption"]],
        effect_size=True,
        verbal_indicators=False,
        interpretation=None,
        number_columns=False,
        plots=False,
        plot_significant_only=True,
    )
    data = Data.initialize_from_dataframe(case["data"]())
    original = DATA_MANAGER.get_data_from_data_label
    DATA_MANAGER.get_data_from_data_label = lambda *a, **k: data
    try:
        result = PairedResult(unique_id=1, settings_panel_index=0, config=cfg)
        recalculate_paired_study(None, result, lambda _p: None)
    finally:
        DATA_MANAGER.get_data_from_data_label = original

    kind = case["kind"]
    supplements = [s for s in result.numeric_supplements() if s.get("kind") == kind]
    if not supplements:
        raise AssertionError(f"{case['study']}: no '{kind}' supplement (error={result.error_message!r})")
    supplement = supplements[0]

    if kind in _POSTHOC_KINDS:
        return {"error": "", "pairs": {pair: _clean(p) for pair, p in supplement["pairs"].items()}}

    if kind == "paired_descriptives":
        rows = {
            row["condition"]: {
                "n": row["n"],
                "mean": _clean(row["mean"]),
                "sd": _clean(row["sd"]),
                "median": _clean(row["median"]),
                "iqr": _clean(row["iqr"]),
            }
            for row in supplement["rows"]
        }
        return {"error": "", "rows": rows}

    if kind == "paired_normality":
        if "differences" in supplement:
            d = supplement["differences"]
            return {"error": "", "differences": {"w": _clean(d["w"]), "p": _clean(d["p"])}}
        conditions = {
            row["condition"]: {"w": _clean(row["w"]), "p": _clean(row["p"])} for row in supplement["conditions"]
        }
        sph = supplement["sphericity"]
        return {"error": "", "conditions": conditions, "sphericity": {"w": _clean(sph["w"]), "p": _clean(sph["p"])}}

    return {"error": "", **{field: _clean(supplement[field]) for field in _FIELDS[kind]}}


def run_case(case: dict, benchmarks: dict) -> BenchmarkCaseResult:
    actual = paired_payload(case)
    expected = benchmarks["studies"][case["study"]]
    comparisons = compare_payloads(
        actual,
        expected,
        tolerance=benchmarks.get("tolerance", 1e-8),
        relative_tolerance=RELATIVE_TOLERANCES.get(case["study"]),
    )
    return BenchmarkCaseResult(MODULE, case["study"], BENCHMARK_PATH, GENERATOR_PATH, comparisons)


def run_paired_benchmarks() -> list[BenchmarkCaseResult]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Missing paired R benchmark file: {BENCHMARK_PATH}\n"
            "Run: ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks"
        )
    benchmarks = load_json(BENCHMARK_PATH)
    return [run_case(case, benchmarks) for case in CASES]


def main() -> int:
    results = run_paired_benchmarks()
    report = render_report(results, HERE / "paired_benchmark_report.html")
    failed = [result for result in results if not result.passed]
    print(f"Paired benchmark report written to {report}")
    if failed:
        print(f"{len(failed)} paired benchmark study/studies failed.")
        return 1
    print("All paired benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
