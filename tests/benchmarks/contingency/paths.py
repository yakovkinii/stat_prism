from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK_PATH = HERE / "benchmarks" / "contingency_r_benchmarks.json"
GENERATOR_PATH = HERE / "r" / "generate_contingency_benchmarks.R"
