from tests.benchmarks.paired.run import run_paired_benchmarks


def test_paired_r_benchmarks():
    results = run_paired_benchmarks()
    failed = [result for result in results if not result.passed]
    details = []
    for result in failed:
        bad = [comparison for comparison in result.comparisons if not comparison.passed]
        details.append(
            f"{result.study}: "
            + "; ".join(f"{item.path} actual={item.actual} expected={item.expected}" for item in bad[:8])
        )
    assert not failed, "\n".join(details)
