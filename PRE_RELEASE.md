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
3. Optional: Regenerate numeric R benchmarks
   ```bash
    $env:STATPRISM_RSCRIPT = "C:/PROGRA~1/R/R-42~1.0/bin/Rscript.exe"
   ```
   ```bash
   ./venv_39/Scripts/python.exe -m tests.benchmarks.regenerate_all_benchmarks
   ```
4. Run numeric benchmark tests and generate the full HTML report
   ```bash
   ./venv_39/Scripts/python.exe -m tests.benchmarks.run_all_tests_and_generate_full_report
   ```
   ```bash
   Invoke-Item tests/benchmarks/reports/full_benchmark_report.html
   ```
5. **Fill in** `RELEASE_NOTES.md` for the new version.
6. Build the user guide and review it locally — English and Ukrainian (first run also installs
   the docs deps into `venv_39`). The online language-toggle button is added by Read the Docs
   on deploy; locally each language is a separate build.
   ```bash
   ./venv_39/Scripts/python.exe -m pip install -r docs/requirements.txt
   ```
   ```bash
   ./venv_39/Scripts/python.exe -m sphinx -b html docs docs/_build/html
   ```
   ```bash
   ./venv_39/Scripts/python.exe -m sphinx -b html -D language=uk docs docs/_build/html-uk
   ```
   ```bash
   Invoke-Item docs/_build/html/index.html
   ```
   ```bash
   Invoke-Item docs/_build/html-uk/index.html
   ```
7. After reviewing, clean up the generated docs
   ```bash
   Remove-Item -Recurse -Force docs/_build
   ```
