from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK_PATH = HERE / "benchmarks" / "reliability_r_benchmarks.json"
GENERATOR_PATH = HERE / "r" / "generate_reliability_benchmarks.R"
