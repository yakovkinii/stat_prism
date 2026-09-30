from __future__ import annotations

import sys

from tests.benchmarks.common import DEFAULT_REPORT, render_report
from tests.benchmarks.reliability.run import run_reliability_benchmarks


def run_all() -> list:
    results = []
    results.extend(run_reliability_benchmarks())
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
