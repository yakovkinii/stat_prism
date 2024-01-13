# python setup.py build
# python setup.py bdist_msi
import sys

from cx_Freeze import Executable, setup

build_exe_options = {
    "excludes": ["tkinter", "unittest"],
    "zip_include_packages": ["encodings", "PySide6"],
}

base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="StatPrism",
    version="0.4",
    description="StatPrism - Speak Stats",
    options={"build_exe": build_exe_options},
    executables=[
        Executable("main.py", base=base, icon="icon.ico", target_name="StatPrism.exe")
    ],
)
