@echo off
rem Build the user guide locally to preview it (HTML). Publishing is done by Read the Docs.
cd /d "%~dp0"

rem Use a dedicated venv so the docs tools don't touch the app environment (venv_39).
if not exist "venv_docs\Scripts\python.exe" (
    py -3 -m venv venv_docs
)
call "venv_docs\Scripts\python.exe" -m pip install -r docs\requirements.txt --disable-pip-version-check
call "venv_docs\Scripts\python.exe" -m sphinx -b html docs docs\_build\html

start "" "docs\_build\html\index.html"
@pause
