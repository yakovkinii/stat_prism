#  Copyright (c) 2023 StatPrism Team. All rights reserved.

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
# nuitka-project-if: {OS} == "Windows":
#    nuitka-project: --windows-console-mode=force
#    nuitka-project: --windows-icon-from-ico={MAIN_DIRECTORY}/resources/StatPrism_icon_small.ico
#    nuitka-project: --product-name=StatPrism
#    nuitka-project: --file-description=StatPrism
#    nuitka-project: --file-version={APP_VERSION}
#    nuitka-project: --product-version={APP_VERSION}

# pre-import because dynamic import causes crashes on win11
from PySide6.QtWebEngineWidgets import QWebEngineView

_ = QWebEngineView

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
    pixmap = QPixmap(":/mat/resources/banner29.png")
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

    from yatools import logging_config

    logging_config.init(logging.INFO)

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
