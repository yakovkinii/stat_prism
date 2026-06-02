@echo off
start "" "%~dp0venv_39\Scripts\pythonw.exe" "%~dp0launcher.py" %1 >> "%~dp0log.log" 2>&1