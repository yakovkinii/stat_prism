from __future__ import annotations

import math

from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report
from tests.benchmarks.reliability.cases import CASES
from tests.benchmarks.reliability.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE

MODULE = "reliability"
# On binary / latent item matrices (phi, tetrachoric, polychoric) two things make omega diverge
# slightly from psych by ~0.1-0.2% (far below any reported precision), both numerical, not
# methodological: (a) StatPrism estimates the latent matrix pairwise then smooths while psych fits
# jointly, and (b) omega's single-common-factor minres fit on these near-Heywood matrices is
# implementation-sensitive (factor_analyzer vs psych). The product-moment / rank coefficients
# (pearson, spearman, kendall, tau-c) match tightly at the default 1e-6. alpha and the item-rest
# stats also match tightly; only omega needs the relative gap, but it is set per study.
RELATIVE_TOLERANCES = {
    "phi_binary_items_with_omega": 2e-3,
    "tetrachoric_binary_items_with_omega": 2e-3,
    "polychoric_likert_items_with_omega": 2e-3,
}


def _clean_number(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def _build_data(case):
    from src.common.constant import ColumnType
    from src.data.data import Data

    data = Data.initialize_from_dataframe(case["data"]())
    for column_name, order in (case.get("ordinal_order") or {}).items():
        column = data[column_name]
        column.column_type = ColumnType.ORDINAL
        column.is_numeric = False
        column.order = {value: index for index, value in enumerate(order, start=1)}
    return data


def reliability_payload(case: dict) -> dict:
    # Drive the real recalculate_reliability_study and read the supplements it attaches to its tables.
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.data.data_manager import DATA_MANAGER
    from src.side_area_panel.modules.reliability.reliability_main import recalculate_reliability_study
    from src.side_area_panel.modules.reliability.reliability_result import ReliabilityResult, ReliabilityStudyConfig

    cfg = ReliabilityStudyConfig(**vars(case["config"]()))
    data = _build_data(case)
    original = DATA_MANAGER.get_data_from_data_label
    DATA_MANAGER.get_data_from_data_label = lambda *a, **k: data
    try:
        result = ReliabilityResult(unique_id=1, settings_panel_index=0, config=cfg)
        recalculate_reliability_study(None, result, lambda _p: None)
    finally:
        DATA_MANAGER.get_data_from_data_label = original

    supplements = result.numeric_supplements()
    scale = next(s for s in supplements if s.get("kind") == "reliability_scale")
    items = next(s for s in supplements if s.get("kind") == "reliability_items")["items"]
    return {
        "error": "",
        "scale": {
            "n_items": scale["n_items"],
            "alpha": _clean_number(scale["alpha"]),
            "omega": _clean_number(scale["omega"]),
        },
        "items": [
            {
                "name": item.name,
                "item_rest": _clean_number(item.item_rest),
                "alpha_deleted": _clean_number(item.alpha_deleted),
                "omega_deleted": _clean_number(item.omega_deleted),
            }
            for item in items
        ],
    }


def run_case(case: dict, benchmarks: dict) -> BenchmarkCaseResult:
    study = case["study"]
    actual = reliability_payload(case)
    expected = benchmarks["studies"][study]
    comparisons = compare_payloads(
        actual,
        expected,
        tolerance=benchmarks.get("tolerance", 1e-8),
        relative_tolerance=RELATIVE_TOLERANCES.get(study),
    )
    return BenchmarkCaseResult(MODULE, study, BENCHMARK_PATH, GENERATOR_PATH, comparisons)


def run_reliability_benchmarks() -> list[BenchmarkCaseResult]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Missing reliability R benchmark file: {BENCHMARK_PATH}\n"
            "Run: ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks"
        )
    benchmarks = load_json(BENCHMARK_PATH)
    return [run_case(case, benchmarks) for case in CASES]


def main() -> int:
    results = run_reliability_benchmarks()
    report = render_report(results, HERE / "reliability_benchmark_report.html")
    failed = [result for result in results if not result.passed]
    print(f"Reliability benchmark report written to {report}")
    if failed:
        print(f"{len(failed)} reliability benchmark study/studies failed.")
        return 1
    print("All reliability benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
