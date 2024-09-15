@setlocal

set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

@for /f "tokens=2 delims==" %%a in ('"wmic os get localdatetime /value"') do @set datetime=%%a

@set datetime=%datetime:~0,4%%datetime:~4,2%%datetime:~6,2%_%datetime:~8,2%%datetime:~10,2%%datetime:~12,2%

:: Read the version from about.py
for /f "tokens=3 delims= " %%v in ('type src\about.py ^| findstr version') do @set version=%%v

:: Remove quotes from the version string
set version=%version:~1,-1%

set logfile=log_%version%_%datetime%.log
set file_path=%1
powershell -Command "Start-Transcript -Path %logfile%; venv_39\Scripts\python.exe launcher.py %file_path%; Stop-Transcript"

@endlocal

