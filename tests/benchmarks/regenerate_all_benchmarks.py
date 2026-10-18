from __future__ import annotations

import sys

from tests.benchmarks.cluster_analysis.regenerate_benchmarks import regenerate_cluster_analysis_benchmarks
from tests.benchmarks.confirmatory_factor_analysis.regenerate_benchmarks import (
    regenerate_confirmatory_factor_analysis_benchmarks,
)
from tests.benchmarks.contingency.regenerate_benchmarks import regenerate_contingency_benchmarks
from tests.benchmarks.correlation.regenerate_benchmarks import regenerate_correlation_benchmarks
from tests.benchmarks.descriptives.regenerate_benchmarks import regenerate_descriptives_benchmarks
from tests.benchmarks.exploratory_factor_analysis.regenerate_benchmarks import (
    regenerate_exploratory_factor_analysis_benchmarks,
)
from tests.benchmarks.general_sem.regenerate_benchmarks import regenerate_general_sem_benchmarks
from tests.benchmarks.mean_comparison.regenerate_benchmarks import regenerate_mean_comparison_benchmarks
from tests.benchmarks.multiple_response.regenerate_benchmarks import regenerate_multiple_response_benchmarks
from tests.benchmarks.paired.regenerate_benchmarks import regenerate_paired_benchmarks
from tests.benchmarks.power_analysis.regenerate_benchmarks import regenerate_power_analysis_benchmarks
from tests.benchmarks.regression.regenerate_benchmarks import regenerate_regression_benchmarks
from tests.benchmarks.reliability.regenerate_benchmarks import regenerate_reliability_benchmarks


def main() -> int:
    try:
        regenerate_reliability_benchmarks()
        regenerate_correlation_benchmarks()
        regenerate_descriptives_benchmarks()
        regenerate_mean_comparison_benchmarks()
        regenerate_paired_benchmarks()
        regenerate_contingency_benchmarks()
        regenerate_regression_benchmarks()
        regenerate_multiple_response_benchmarks()
        regenerate_power_analysis_benchmarks()
        regenerate_cluster_analysis_benchmarks()
        regenerate_exploratory_factor_analysis_benchmarks()
        regenerate_confirmatory_factor_analysis_benchmarks()
        regenerate_general_sem_benchmarks()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("All benchmark files regenerated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
