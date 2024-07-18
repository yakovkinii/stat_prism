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

    def my_exception_hook(exctype, value, traceback):
        # Print the error and traceback
        print(exctype, value, traceback)
        # Call the normal Exception hook after
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook

    # Set icon
    from PySide6.QtGui import QIcon

    app.setWindowIcon(QIcon(":/mat/resources/Icon.ico"))

    # Load all modules
    logging.info("Loading all modules")
    from main import load_all

    main_win = load_all()

    # Show window after loading
    from PySide6.QtCore import QTimer

    delta_time = time.time() - time0
    logging.info(f"Time to load: {delta_time} seconds")
    splash_time = int(max(10.0, 1500-delta_time*1000))
    QTimer.singleShot(splash_time, splash.close)
    QTimer.singleShot(splash_time, main_win.showMaximized)
    app.exec()
