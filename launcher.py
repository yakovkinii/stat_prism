#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.

# Nuitka build configuration. Build with:
#   python -m nuitka launcher.py
#
# nuitka-project-set: APP_VERSION = __import__("src.about", fromlist=["version"]).version
# nuitka-project: --mode=standalone
# nuitka-project: --output-dir={MAIN_DIRECTORY}/build/nuitka
# nuitka-project: --remove-output
# nuitka-project: --python-flag=unbuffered
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --enable-plugin=matplotlib
# nuitka-project: --include-package=src
# nuitka-project: --include-module=main
# nuitka-project: --include-module=resources_rc
# nuitka-project: --include-package=qtawesome
# nuitka-project: --include-package-data=qtawesome
# nuitka-project: --include-package-data=matplotlib
# nuitka-project: --include-package-data=pandas
# nuitka-project: --include-package-data=openpyxl
# nuitka-project: --include-package-data=pyarrow
# nuitka-project: --include-package-data=sklearn
# nuitka-project: --include-package-data=scipy
# nuitka-project: --include-package-data=statsmodels
# nuitka-project: --include-package-data=pingouin
# nuitka-project: --include-package-data=scikit_posthocs
# nuitka-project: --include-package-data=factor_analyzer
# nuitka-project: --include-package=semopy
# nuitka-project: --include-package-data=semopy
# nuitka-project: --include-package=sympy
# nuitka-project: --include-package-data=sympy
# Exclude every package's test/benchmark subpackages. sympy's in particular ship huge
# auto-generated modules (sympy.polys.tests.test_rootoftools, sympy.polys.benchmarks.bench_solvers)
# whose .c files exhaust the MSVC compiler heap (fatal error C1060/C1002). None are needed at
# runtime, and skipping them also shrinks the build. --nofollow-import-to overrides the
# --include-package above for the matched modules.
# nuitka-project: --nofollow-import-to=*.tests
# nuitka-project: --nofollow-import-to=*.benchmarks
# nuitka-project: --nofollow-import-to=sympy.testing
# nuitka-project-if: {OS} == "Windows":
#    nuitka-project: --windows-console-mode=disable
#    nuitka-project: --output-filename=StatPrism.exe
#    nuitka-project: --windows-icon-from-ico={MAIN_DIRECTORY}/resources/icon.ico
#    nuitka-project: --product-name=StatPrism
#    nuitka-project: --file-description=StatPrism
#    nuitka-project: --file-version={APP_VERSION}
#    nuitka-project: --product-version={APP_VERSION}

# pre-import because dynamic import causes crashes on win11
from PySide6.QtWebEngineWidgets import QWebEngineView

_ = QWebEngineView


def _setup_logging(level=None):
    """Send logs to a single file that is overwritten on each launch (the packaged app runs with
    no console, so a file is the only place logs can go). The file sits next to the executable
    when packaged, falling back to %LOCALAPPDATA%\\StatPrism if that directory is read-only (e.g.
    an install under Program Files). A coloured console handler is added only when a real stderr
    exists (source runs / console builds)."""
    import logging
    import os
    import sys
    from pathlib import Path

    if level is None:
        level = logging.INFO

    base = Path(sys.executable).resolve().parent if "__compiled__" in globals() else Path.cwd()
    formatter = logging.Formatter("%(asctime)s %(levelname).4s %(name)s: %(message)s", "%H:%M:%S")
    root = logging.getLogger()
    root.setLevel(level)

    local_appdata = os.environ.get("LOCALAPPDATA", str(base))
    for path in (base / "statprism.log", Path(local_appdata) / "StatPrism" / "statprism.log"):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(path, mode="w", encoding="utf-8")  # truncate each launch
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)
            break
        except Exception:
            continue

    # Console logging only where there is a console to print to.
    if sys.stderr is not None:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        root.addHandler(stream_handler)


if __name__ == "__main__":
    import time

    time0 = time.time()

    import sys

    from PySide6.QtGui import QPixmap
    from PySide6.QtWidgets import QApplication, QSplashScreen

    import resources_rc

    _ = resources_rc

    import os

    # Qt-free, so it is safe to import before the QApplication exists.
    from src.common.ui_theme import IS_DARK_THEME

    if sys.platform == "win32":
        # Match the window chrome (title bar) to the active UI theme. Must be set before the
        # QApplication is constructed.
        os.environ.setdefault("QT_QPA_PLATFORM", f"windows:darkmode={'2' if IS_DARK_THEME else '0'}")

    app = QApplication(sys.argv)
    pixmap = QPixmap(":/mat/resources/splash.png")

    from PySide6.QtGui import QColor, QFont, QPainter

    from src.about import version

    version_painter = QPainter(pixmap)
    version_painter.setPen(QColor("#eedd88"))
    version_font = QFont()
    version_font.setPointSize(20)
    version_painter.setFont(version_font)
    version_painter.drawText(90, 257, f"v{version}")
    version_painter.end()

    splash = QSplashScreen(pixmap)
    splash.show()

    # Loading line drawn along the bottom of the splash; extended after each
    # import in src/ui_main.py finishes (see report_splash_progress).
    from PySide6.QtGui import QColor, QPainter

    from src.common.progress import set_splash_callback

    def _update_splash_progress(value, maximum):
        fraction = value / max(maximum, 1)
        frame = pixmap.copy()
        painter = QPainter(frame)
        painter.fillRect(40, frame.height() - 24, int((frame.width() - 80) * fraction), 2, QColor("#eedd88"))
        painter.end()
        splash.setPixmap(frame)
        app.processEvents()

    set_splash_callback(_update_splash_progress)
    app.processEvents()

    # ================= Set Global Styles =================
    from PySide6.QtWidgets import QStyleFactory

    app.setStyle(QStyleFactory.create("Fusion"))

    # Force the color scheme matching the active UI theme where the setter exists (Qt 6.8+);
    # for Qt 6.5-6.7 the QT_QPA_PLATFORM darkmode option above already requests it.
    try:
        from PySide6.QtCore import Qt as _Qt

        app.styleHints().setColorScheme(_Qt.ColorScheme.Dark if IS_DARK_THEME else _Qt.ColorScheme.Light)
    except (AttributeError, TypeError, ImportError):
        pass

    from PySide6.QtGui import QPalette

    from src.pyside_ext.styling import Style

    pal = app.style().standardPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(Style.Color.BackgroundElevated.value))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(Style.Color.Text.value))
    pal.setColor(QPalette.ColorRole.Button, QColor(Style.Color.BackgroundElevated.value))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(Style.Color.Text.value))
    pal.setColor(QPalette.ColorRole.Base, QColor(Style.Color.BackgroundEdit.value))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(Style.Color.BackgroundElevated.value))
    pal.setColor(QPalette.ColorRole.Text, QColor(Style.Color.Text.value))
    pal.setColor(QPalette.ColorRole.PlaceholderText, QColor(Style.Color.SecondaryText.value))
    pal.setColor(QPalette.ColorRole.ToolTipBase, QColor(Style.Color.BackgroundElevated.value))
    pal.setColor(QPalette.ColorRole.ToolTipText, QColor(Style.Color.Text.value))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(Style.Color.Selection.value))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(Style.Color.Text.value))
    # Disabled-state text, so greyed controls remain legible on the dark chrome.
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(Style.Color.SecondaryText.value))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(Style.Color.SecondaryText.value))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(Style.Color.SecondaryText.value))
    app.setPalette(pal)
    import logging

    _setup_logging(logging.INFO)

    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook
    main_win = None

    def my_exception_hook(exctype, value, traceback):
        import traceback as tb

        global win_main

        logging.error("".join(tb.format_exception(exctype, value, traceback)))

        # Call the normal Exception hook after
        sys._excepthook(exctype, value, traceback)

        # if main_win is not None:
        #     logging.info("Recovering the project after crash ...")
        #     if main_win.current_file_path is not None:
        #         main_win.current_file_path += ".recovered.sp"
        #     else:
        #         import os
        #
        #         main_win.current_file_path = os.path.abspath("recovered.sp")
        #
        #     logging.debug("Saving recovered project to:")
        #     logging.debug(main_win.current_file_path)
        #
        #     from src.side_area_panel.registry import PanelRegistry
        #
        #     PanelRegistry.HOME.ui_instance.save_handler()
        #
        #     logging.error(
        #         f"StatPrism crashed, but the project was recovered and saved to: {main_win.current_file_path}"
        #     )
        #
        #     from PySide6.QtWidgets import QMessageBox
        #
        #     msg = QMessageBox()
        #     msg.setIcon(QMessageBox.Icon.Critical)
        #     msg.setText(f"StatPrism crashed. The project was recovered and saved to:\n{main_win.current_file_path}")
        #     msg.setWindowTitle("Oops... StatPrism crashed")
        #     msg.setDetailedText("\n".join(tb.format_exception(exctype, value, traceback)))
        #
        #     msg.setStandardButtons(QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Abort)
        #     msg.setDefaultButton(QMessageBox.StandardButton.Ignore)
        #     ret = msg.exec()
        #     if ret == QMessageBox.StandardButton.Ignore:
        #         logging.warning("Ignoring the crash")
        #         return

        sys.exit(1)

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook

    # Set app id for windows taskbar
    import ctypes

    from src.about import version

    myappid = f"stat_prism_{version}"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # Load all modules
    logging.info("Loading all modules")
    from main import load_all

    main_win = load_all()

    # Show window after loading
    from PySide6.QtCore import QTimer

    delta_time = time.time() - time0
    logging.info(f"Time to load: {delta_time} seconds")
    splash_time = int(max(10.0, 1500 - delta_time * 1000))
    QTimer.singleShot(splash_time, splash.close)
    QTimer.singleShot(
        splash_time,
        lambda: main_win.init_web_view_and_show_maximized(file_path=sys.argv[1] if len(sys.argv) > 1 else None),
    )
    app.exec()
