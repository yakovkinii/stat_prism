from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK_PATH = HERE / "benchmarks" / "exploratory_factor_analysis_r_benchmarks.json"
GENERATOR_PATH = HERE / "r" / "generate_exploratory_factor_analysis_benchmarks.R"
