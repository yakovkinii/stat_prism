from __future__ import annotations

import sys

from tests.benchmarks.reliability.regenerate_benchmarks import regenerate_reliability_benchmarks


def main() -> int:
    try:
        regenerate_reliability_benchmarks()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("All benchmark files regenerated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
