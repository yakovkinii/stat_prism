from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK_PATH = HERE / "benchmarks" / "general_sem_r_benchmarks.json"
GENERATOR_PATH = HERE / "r" / "generate_general_sem_benchmarks.R"
