from __future__ import annotations

import sys

from tests.benchmarks.correlation.regenerate_benchmarks import regenerate_correlation_benchmarks
from tests.benchmarks.descriptives.regenerate_benchmarks import regenerate_descriptives_benchmarks
from tests.benchmarks.mean_comparison.regenerate_benchmarks import regenerate_mean_comparison_benchmarks
from tests.benchmarks.reliability.regenerate_benchmarks import regenerate_reliability_benchmarks


def main() -> int:
    try:
        regenerate_reliability_benchmarks()
        regenerate_correlation_benchmarks()
        regenerate_descriptives_benchmarks()
        regenerate_mean_comparison_benchmarks()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("All benchmark files regenerated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
