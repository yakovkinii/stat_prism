# Release checklist

Assumes the dev environment (`venv_39`) is checked out and populated.

1. Check (dry run, writes nothing)
   ```bash
   ./venv_39/Scripts/python.exe tools/release.py patch --check
   ```
2. Bump version and run formatters (pick one)
   ```bash
   ./venv_39/Scripts/python.exe tools/release.py patch
   ```
   ```bash
   ./venv_39/Scripts/python.exe tools/release.py minor
   ```
   ```bash
   ./venv_39/Scripts/python.exe tools/release.py major
   ```
3. Regenerate numeric R benchmarks (only when intentionally updating benchmark values)
   ```powershell
   $env:STATPRISM_RSCRIPT = "C:/PROGRA~1/R/R-42~1.0/bin/Rscript.exe"
   ```
   ```bash
   ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks
   ```
   Requires the R packages used by the benchmark generators (currently `jsonlite`
   and `psych` for Reliability). `STATPRISM_RSCRIPT` avoids any global PATH edits.
4. Run numeric benchmark tests and generate the full HTML report
   ```bash
   ./venv_39/Scripts/python.exe -m tests.benchmarks.run_all_tests_and_generate_full_report
   ```
   The report is written to `tests/benchmarks/reports/full_benchmark_report.html`.
   Open it in the default browser:
   ```powershell
   Invoke-Item tests/benchmarks/reports/full_benchmark_report.html
   ```
5. **Fill in** `RELEASE_NOTES.md` for the new version.
