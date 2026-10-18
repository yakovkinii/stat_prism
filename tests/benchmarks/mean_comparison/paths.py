from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK_PATH = HERE / "benchmarks" / "mean_comparison_r_benchmarks.json"
GENERATOR_PATH = HERE / "r" / "generate_mean_comparison_benchmarks.R"
