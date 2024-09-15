@echo off
REM Batch script to associate .sp files with a batch file and set a custom icon

REM Define paths
set BAT_FILE_PATH=%~dp0_RUN.bat
set ICON_FILE_PATH=%~dp0resources\Icon.ico
set "REG_BAT_FILE_PATH=%BAT_FILE_PATH:\=\\%"
set "REG_ICON_FILE_PATH=%ICON_FILE_PATH:\=\\%"

REM Associate .sp files. Likely redundant but anyway
assoc .sp=StatPrismProjectFile

REM Define the command to run when an .sp file is opened. Likely redundant but anyway
ftype StatPrismProjectFile="%BAT_FILE_PATH%" "%%1"

(
echo Windows Registry Editor Version 5.00
echo.
echo [HKEY_CLASSES_ROOT\.sp]
echo @="StatPrismProjectFile"
echo.
echo [HKEY_CLASSES_ROOT\StatPrismProjectFile]
echo @="StatPrism Project File"
echo.
echo [HKEY_CLASSES_ROOT\StatPrismProjectFile\DefaultIcon]
echo @="%REG_ICON_FILE_PATH%"
echo.
echo [HKEY_CLASSES_ROOT\StatPrismProjectFile\Shell\Open\Command]
echo @="\"%REG_BAT_FILE_PATH%\" \"%%1\""
) > "./spfile_association.reg"

REM Import the .reg file to update the registry
regedit /s "./spfile_association.reg"

REM Clean up
del "./spfile_association.reg"

echo Association complete. The changes will take effect after a restart.
pause
