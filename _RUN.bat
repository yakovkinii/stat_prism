@setlocal

@for /f "tokens=2 delims==" %%a in ('"wmic os get localdatetime /value"') do @set datetime=%%a

@set datetime=%datetime:~0,4%%datetime:~4,2%%datetime:~6,2%_%datetime:~8,2%%datetime:~10,2%%datetime:~12,2%

set logfile=log_%datetime%.log

powershell -Command "Start-Transcript -Path %logfile%; venv_39\Scripts\python.exe launcher.py; Stop-Transcript"

@endlocal

