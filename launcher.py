#  Copyright (c) 2023 StatPrism Team. All rights reserved.


if __name__ == "__main__":
    import time

    time0 = time.time()

    import sys

    from PySide6.QtGui import QPixmap
    from PySide6.QtWidgets import QApplication, QSplashScreen

    import resources_rc

    _ = resources_rc

    app = QApplication(sys.argv)
    pixmap = QPixmap(":/mat/resources/banner22.png")
    splash = QSplashScreen(pixmap)
    splash.show()

    # ================= Set Global Styles =================
    from PySide6.QtWidgets import QStyleFactory

    app.setStyle(QStyleFactory.create("Fusion"))

    from PySide6.QtGui import QColor, QPalette

    from src.pyside_ext.styling import Style

    pal = app.style().standardPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(Style.Color.BackgroundElevated.value))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(Style.Color.Text.value))
    pal.setColor(QPalette.ColorRole.Button, QColor(Style.Color.BackgroundElevated.value))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(Style.Color.Text.value))
    pal.setColor(QPalette.ColorRole.Base, QColor(Style.Color.BackgroundEdit.value))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(Style.Color.BackgroundEdit.value))
    pal.setColor(QPalette.ColorRole.Text, QColor(Style.Color.Text.value))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(Style.Color.Highlight.value))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(Style.Color.Text.value))

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
        #     from src.settings_panel.registry import PanelRegistry
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
