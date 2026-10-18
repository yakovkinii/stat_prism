from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK_PATH = HERE / "benchmarks" / "paired_r_benchmarks.json"
GENERATOR_PATH = HERE / "r" / "generate_paired_benchmarks.R"
