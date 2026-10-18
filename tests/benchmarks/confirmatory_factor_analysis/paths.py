from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK_PATH = HERE / "benchmarks" / "confirmatory_factor_analysis_r_benchmarks.json"
GENERATOR_PATH = HERE / "r" / "generate_confirmatory_factor_analysis_benchmarks.R"
