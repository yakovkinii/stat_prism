from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK_PATH = HERE / "benchmarks" / "descriptives_r_benchmarks.json"
GENERATOR_PATH = HERE / "r" / "generate_descriptives_benchmarks.R"
