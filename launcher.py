#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#

# fading_splash.py
from PySide6.QtCore import QVariantAnimation, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QSplashScreen, QApplication

class FadingSplash(QSplashScreen):
    def __init__(self, pm: QPixmap, flags=Qt.SplashScreen):
        super().__init__(pm, flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._current = pm
        self._next = QPixmap()
        self._progress = 0.0

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(500)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.valueChanged.connect(self._on_value)
        self._anim.finished.connect(self._on_finished)

    def fadeTo(self, pm: QPixmap, duration_ms: int = 500):
        self._next = pm
        self._anim.stop()
        self._anim.setDuration(duration_ms)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    # ----- internals -----
    def _on_value(self, v):
        self._progress = float(v)
        self.update()

    def _on_finished(self):
        self._current = self._next
        self._next = QPixmap()
        self._progress = 0.0
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)

        p.setOpacity(1.0)
        p.drawPixmap(0, 0, self._current)

        if not self._next.isNull():
            p.setOpacity(self._progress)
            p.drawPixmap(0, 0, self._next)




if __name__ == "__main__":
    import sys

    from PySide6.QtGui import QPixmap
    from PySide6.QtWidgets import QApplication, QSplashScreen

    import resources_rc

    _ = resources_rc

    app = QApplication(sys.argv)
    pixmap = QPixmap(":/mat/resources/banner.png")
    splash = FadingSplash(pixmap)
    splash.show()
    app.processEvents()

    # ================= Set Global Styles =================
    from PySide6.QtWidgets import QStyleFactory
    app.setStyle(QStyleFactory.create("Fusion"))

    from PySide6.QtGui import QPalette, QColor
    from src.pyside_ext.styling import Style
    pal = app.style().standardPalette()
    pal.setColor(QPalette.Window, QColor(Style.Color.BackgroundElevated.value))
    pal.setColor(QPalette.WindowText, QColor(Style.Color.Text.value))
    pal.setColor(QPalette.Button, QColor(Style.Color.BackgroundElevated.value))
    pal.setColor(QPalette.ButtonText, QColor(Style.Color.Text.value))
    pal.setColor(QPalette.Base, QColor(Style.Color.BackgroundEdit.value))
    pal.setColor(QPalette.AlternateBase, QColor(Style.Color.BackgroundEdit.value))
    pal.setColor(QPalette.Text, QColor(Style.Color.Text.value))
    pal.setColor(QPalette.Highlight, QColor(Style.Color.Highlight.value))
    pal.setColor(QPalette.HighlightedText, QColor(Style.Color.Text.value))


    import time

    time0 = time.time()

    import logging

    from yatools import logging_config

    logging_config.init(logging.WARNING)

    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook
    main_win = None

    def my_exception_hook(exctype, value, traceback):
        import traceback as tb

        global win_main

        logging.error("".join(tb.format_exception(exctype, value, traceback)))

        # Call the normal Exception hook after
        sys._excepthook(exctype, value, traceback)

        if main_win is not None:
            logging.info("Recovering the project after crash ...")
            if main_win.current_file_path is not None:
                main_win.current_file_path += ".recovered.sp"
            else:
                import os

                main_win.current_file_path = os.path.abspath("recovered.sp")

            logging.debug("Saving recovered project to:")
            logging.debug(main_win.current_file_path)

            from src.settings_panel.panels.registry import PanelRegistry

            PanelRegistry.HOME.ui_instance.save_handler()

            logging.error(
                f"StatPrism crashed, but the project was recovered and saved to: {main_win.current_file_path}"
            )

            from PySide6.QtWidgets import QMessageBox

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText(f"StatPrism crashed. The project was recovered and saved to:\n{main_win.current_file_path}")
            msg.setWindowTitle("Oops... StatPrism crashed")
            msg.setDetailedText("\n".join(tb.format_exception(exctype, value, traceback)))

            msg.setStandardButtons(QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Abort)
            msg.setDefaultButton(QMessageBox.StandardButton.Ignore)
            ret = msg.exec()
            if ret == QMessageBox.StandardButton.Ignore:
                logging.warning("Ignoring the crash")
                return

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
