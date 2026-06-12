@echo off
if "%~1"=="" (
    start "" /D "%~dp0" "%~dp0venv_39\Scripts\pythonw.exe" "%~dp0launcher.py"
) else (
    start "" /D "%~dp0" "%~dp0venv_39\Scripts\pythonw.exe" "%~dp0launcher.py" "%~1"
)
