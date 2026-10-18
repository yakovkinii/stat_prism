from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK_PATH = HERE / "benchmarks" / "multiple_response_r_benchmarks.json"
GENERATOR_PATH = HERE / "r" / "generate_multiple_response_benchmarks.R"
