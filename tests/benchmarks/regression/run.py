from __future__ import annotations

import math

from tests.benchmarks.common import BenchmarkCaseResult, compare_payloads, load_json, render_report
from tests.benchmarks.regression.cases import CASES, regression_data
from tests.benchmarks.regression.paths import BENCHMARK_PATH, GENERATOR_PATH, HERE

MODULE = "regression"
# statsmodels (Logit/MNLogit MLE) and R (glm/nnet::multinom) use different optimizers; allow a small
# relative slack on the iterative fits while the linear (lm) studies stay at the strict 1e-6.
RELATIVE_TOLERANCES = {
    # statsmodels (Logit/MNLogit Newton) vs R (glm IRLS, nnet::multinom BFGS) converge to the same MLE
    # but differ at the optimizer-tolerance level. Tail p-values and near-zero coefficients drift most,
    # so these use a modest relative slack (still far tighter than any real methodological difference).
    "logistic_fit": 2e-3,
    "logistic_coef": 2e-3,
    "logistic_moderation_coef": 2e-3,
    "multinomial_fit": 5e-3,
    "multinomial_coef": 5e-3,
}
# nnet::multinom's BFGS leaves near-zero (non-significant) coefficients slightly off, where a relative
# tolerance explodes; an absolute floor lets those essentially-zero estimates match.
ABSOLUTE_TOLERANCES = {"multinomial_coef": 5e-3}

_MODEL = {"linear": "Linear (OLS)", "logistic": "Logistic (binary)", "multinomial": "Multinomial (logistic)"}


def _clean(value):
    if value is None:
        return None
    value = float(value)
    return None if math.isnan(value) else value


def _coef_rows(rows):
    return [
        {
            "b": _clean(r["b"]),
            "se": _clean(r["se"]),
            "beta": _clean(r.get("beta")),
            "t": _clean(r["t"]),
            "p": _clean(r["p"]),
        }
        for r in rows
    ]


def _glm_rows(rows):
    return [
        {
            "b": _clean(r["b"]),
            "se": _clean(r["se"]),
            "odds_ratio": _clean(r["odds_ratio"]),
            "z": _clean(r["z"]),
            "p": _clean(r["p"]),
        }
        for r in rows
    ]


def regression_payload(case: dict) -> dict:
    import src.side_area_panel.modules.common.result.registry  # noqa: F401
    from src.data.data import Data
    from src.data.data_manager import DATA_MANAGER
    from src.side_area_panel.modules.regression.regression_main import recalculate_regression_study
    from src.side_area_panel.modules.regression.regression_result import RegressionResult, RegressionStudyConfig

    cfg = RegressionStudyConfig(
        data_source="Auto",
        column_selector=[
            [case["dep"]],
            list(case["indeps"]),
            [case["mod"]] if case.get("mod") else [],
            [case["med"]] if case.get("med") else [],
        ],
        model_type=_MODEL[case["model"]],
        standardized=True,
        verbal_indicators=False,
        interpretation=None,
        diagnostics=True,
        plots=False,
    )
    data = Data.initialize_from_dataframe(regression_data())
    original = DATA_MANAGER.get_data_from_data_label
    DATA_MANAGER.get_data_from_data_label = lambda *a, **k: data
    try:
        result = RegressionResult(unique_id=1, settings_panel_index=0, config=cfg)
        recalculate_regression_study(_Elements(), result, lambda _p: None)
    finally:
        DATA_MANAGER.get_data_from_data_label = original

    kind = case["kind"]
    supplements = [s for s in result.numeric_supplements() if s.get("kind") == kind]
    if not supplements:
        raise AssertionError(f"{case['study']}: no '{kind}' supplement (error={result.error_message!r})")
    s = supplements[0]

    if kind == "regression_linear_fit":
        return {"error": "", **{k: _clean(s[k]) for k in ("n", "r2", "adj_r2", "f", "df_model", "df_resid", "f_p")}}
    if kind == "regression_linear_coef":
        return {"error": "", "rows": _coef_rows(s["rows"])}
    if kind == "regression_vif":
        return {"error": "", "rows": [{"name": r["name"], "vif": _clean(r["vif"])} for r in s["rows"]]}
    if kind == "regression_influence":
        rows = s["rows"]
        ordered = [rows[k] for k in sorted(rows, key=lambda z: int(z))]
        return {
            "error": "",
            "rows": [
                {
                    "mahalanobis": _clean(r["mahalanobis"]),
                    "cooks": _clean(r["cooks"]),
                    "leverage": _clean(r["leverage"]),
                    "std_resid": _clean(r["std_resid"]),
                }
                for r in ordered
            ],
            "dw": _clean(s["dw"]),
        }
    if kind == "regression_paths":
        return {
            "error": "",
            "rows": [
                {
                    "from": r["from"],
                    "to": r["to"],
                    "b": _clean(r["b"]),
                    "se": _clean(r["se"]),
                    "t": _clean(r["t"]),
                    "p": _clean(r["p"]),
                }
                for r in s["rows"]
            ],
            "indirect": [{"predictor": r["predictor"], "value": _clean(r["value"])} for r in s["indirect"]],
        }
    if kind in ("regression_logistic_fit", "regression_multinomial_fit"):
        return {"error": "", **{k: _clean(s[k]) for k in ("n", "pseudo_r2", "llr_chi2", "df_model", "llr_p")}}
    if kind == "regression_logistic_coef":
        return {"error": "", "rows": _glm_rows(s["rows"])}
    # regression_multinomial_coef
    return {"error": "", "blocks": [{"category": b["category"], "rows": _glm_rows(b["rows"])} for b in s["blocks"]]}


class _Elements:
    """Minimal stand-in for the UI Elements object (only column_selector.set_alert is called)."""

    class _ColumnSelector:
        def set_alert(self, _index):
            pass

    def __init__(self):
        self.column_selector = self._ColumnSelector()


def run_case(case: dict, benchmarks: dict) -> BenchmarkCaseResult:
    actual = regression_payload(case)
    expected = benchmarks["studies"][case["study"]]
    comparisons = compare_payloads(
        actual,
        expected,
        tolerance=ABSOLUTE_TOLERANCES.get(case["study"], benchmarks.get("tolerance", 1e-8)),
        relative_tolerance=RELATIVE_TOLERANCES.get(case["study"]),
    )
    return BenchmarkCaseResult(MODULE, case["study"], BENCHMARK_PATH, GENERATOR_PATH, comparisons)


def run_regression_benchmarks() -> list[BenchmarkCaseResult]:
    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(
            f"Missing regression R benchmark file: {BENCHMARK_PATH}\n"
            "Run: ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks"
        )
    benchmarks = load_json(BENCHMARK_PATH)
    return [run_case(case, benchmarks) for case in CASES]


def main() -> int:
    results = run_regression_benchmarks()
    report = render_report(results, HERE / "regression_benchmark_report.html")
    failed = [result for result in results if not result.passed]
    print(f"Regression benchmark report written to {report}")
    if failed:
        print(f"{len(failed)} regression benchmark study/studies failed.")
        return 1
    print("All regression benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
