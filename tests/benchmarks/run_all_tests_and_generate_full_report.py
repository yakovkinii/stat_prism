from __future__ import annotations

import sys

from tests.benchmarks.cluster_analysis.run import run_cluster_analysis_benchmarks
from tests.benchmarks.common import DEFAULT_REPORT, render_report
from tests.benchmarks.confirmatory_factor_analysis.run import run_confirmatory_factor_analysis_benchmarks
from tests.benchmarks.contingency.run import run_contingency_benchmarks
from tests.benchmarks.correlation.run import run_correlation_benchmarks
from tests.benchmarks.descriptives.run import run_descriptives_benchmarks
from tests.benchmarks.exploratory_factor_analysis.run import run_exploratory_factor_analysis_benchmarks
from tests.benchmarks.general_sem.run import run_general_sem_benchmarks
from tests.benchmarks.mean_comparison.run import run_mean_comparison_benchmarks
from tests.benchmarks.multiple_response.run import run_multiple_response_benchmarks
from tests.benchmarks.paired.run import run_paired_benchmarks
from tests.benchmarks.power_analysis.run import run_power_analysis_benchmarks
from tests.benchmarks.regression.run import run_regression_benchmarks
from tests.benchmarks.reliability.run import run_reliability_benchmarks


def run_all() -> list:
    results = []
    results.extend(run_reliability_benchmarks())
    results.extend(run_correlation_benchmarks())
    results.extend(run_descriptives_benchmarks())
    results.extend(run_mean_comparison_benchmarks())
    results.extend(run_paired_benchmarks())
    results.extend(run_contingency_benchmarks())
    results.extend(run_regression_benchmarks())
    results.extend(run_multiple_response_benchmarks())
    results.extend(run_power_analysis_benchmarks())
    results.extend(run_cluster_analysis_benchmarks())
    results.extend(run_exploratory_factor_analysis_benchmarks())
    results.extend(run_confirmatory_factor_analysis_benchmarks())
    results.extend(run_general_sem_benchmarks())
    return results


def main() -> int:
    try:
        results = run_all()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    report_path = render_report(results, DEFAULT_REPORT)
    failed = [result for result in results if not result.passed]
    print(f"Benchmark report written to {report_path}")
    if failed:
        print(f"{len(failed)} benchmark study/studies failed.")
        return 1
    print("All benchmark studies passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
