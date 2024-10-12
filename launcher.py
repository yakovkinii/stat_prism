if __name__ == "__main__":
    import sys

    from PySide6.QtGui import QPixmap
    from PySide6.QtWidgets import QApplication, QSplashScreen

    import resources_rc

    _ = resources_rc

    app = QApplication(sys.argv)
    pixmap = QPixmap(":/mat/resources/StatPrism_splash.png")
    splash = QSplashScreen(pixmap)
    splash.show()
    import time

    time0 = time.time()

    import logging

    from yatools import logging_config

    logging_config.init(logging.DEBUG)

    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook
    main_win = None

    def my_exception_hook(exctype, value, traceback):
        global win_main
        # Print the error and traceback
        print(exctype, value, traceback)
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
            main_win.hide()
            logging.error(
                f"StatPrism crashed, but the project was recovered and saved to: {main_win.current_file_path}"
            )

        # logging.error("Press Enter to exit ...")
        # input()
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
