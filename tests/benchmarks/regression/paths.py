from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK_PATH = HERE / "benchmarks" / "regression_r_benchmarks.json"
GENERATOR_PATH = HERE / "r" / "generate_regression_benchmarks.R"
