@echo off
for /R %%i in (*.qrc) do (
    echo Processing: %%i
    pyrcc5 "%%i" -o "%%~dpni_rc.py"
)
echo Done!