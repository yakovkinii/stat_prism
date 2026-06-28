@echo off
rem Bump the version (single source: src/about.py), run the formatters (black/isort/flake8)
rem and sync README.md + CITATION.cff. Pick exactly one of patch / minor / major.
rem Examples:
rem   _RELEASE.bat patch
rem   _RELEASE.bat minor
rem   _RELEASE.bat major
rem   _RELEASE.bat patch --check        (dry run, writes nothing)
rem   _RELEASE.bat minor --test --docs  (also run the heavier checks)
cd /d "%~dp0"
call "venv_39\Scripts\python.exe" "tools\release.py" %*
