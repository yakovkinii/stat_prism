@echo off
setlocal
REM Associate .sp files with the development launcher for the current Windows user.

set "BAT_FILE_PATH=%~dp0_RUN.bat"
set "ICON_FILE_PATH=%~dp0resources\Icon.ico"

if not exist "%BAT_FILE_PATH%" (
    echo Missing launcher: "%BAT_FILE_PATH%"
    pause
    exit /b 1
)

if not exist "%ICON_FILE_PATH%" (
    echo Missing icon: "%ICON_FILE_PATH%"
    pause
    exit /b 1
)

reg add "HKCU\Software\Classes\.sp" /ve /d "StatPrismProjectFile" /f
if errorlevel 1 goto :failed

reg add "HKCU\Software\Classes\StatPrismProjectFile" /ve /d "StatPrism Project File" /f
if errorlevel 1 goto :failed

reg add "HKCU\Software\Classes\StatPrismProjectFile\DefaultIcon" /ve /d "%ICON_FILE_PATH%" /f
if errorlevel 1 goto :failed

reg add "HKCU\Software\Classes\StatPrismProjectFile\Shell\Open\Command" /ve /d "\"%BAT_FILE_PATH%\" \"%%1\"" /f
if errorlevel 1 goto :failed

echo Association complete. If Explorer has cached the old association, sign out and back in.
pause
exit /b 0

:failed
echo Failed to associate .sp files.
pause
exit /b 1
