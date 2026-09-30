from __future__ import annotations

import os
import subprocess
import shutil
from pathlib import Path

from tests.benchmarks.reliability.paths import BENCHMARK_PATH, GENERATOR_PATH


def regenerate_reliability_benchmarks() -> None:
    configured_rscript = os.environ.get("STATPRISM_RSCRIPT")
    rscript = configured_rscript or shutil.which("Rscript")
    if rscript is None:
        raise RuntimeError(
            "Rscript was not found. Set STATPRISM_RSCRIPT to the full Rscript.exe path, or install R "
            "with Rscript.exe on PATH. Example: "
            "$env:STATPRISM_RSCRIPT='C:/PROGRA~1/R/R-42~1.0/bin/Rscript.exe'"
        )
    if not Path(rscript).exists() and configured_rscript:
        raise RuntimeError(f"STATPRISM_RSCRIPT points to a missing file: {rscript}")
    command = [rscript, str(GENERATOR_PATH), str(BENCHMARK_PATH)]
    subprocess.run(command, check=True)


def main() -> int:
    regenerate_reliability_benchmarks()
    print(f"Reliability benchmarks regenerated at {Path(BENCHMARK_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
