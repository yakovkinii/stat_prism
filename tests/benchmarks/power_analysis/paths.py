from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK_PATH = HERE / "benchmarks" / "power_analysis_r_benchmarks.json"
GENERATOR_PATH = HERE / "r" / "generate_power_analysis_benchmarks.R"
