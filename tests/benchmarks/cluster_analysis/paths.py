from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK_PATH = HERE / "benchmarks" / "cluster_analysis_r_benchmarks.json"
GENERATOR_PATH = HERE / "r" / "generate_cluster_analysis_benchmarks.R"
