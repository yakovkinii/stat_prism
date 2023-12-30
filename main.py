import logging
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen
from yatools import logging_config

from core.mainwindow.ui import MainWindow

if __name__ == "__main__":
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

    app = QApplication(sys.argv)

    pixmap = QPixmap(":/mat/resources/full_black_gold.png")
    splash = QSplashScreen(pixmap)
    splash.show()

    # Instantiate and show the first dialog
    main_win = MainWindow()
    splash_time = 1  # 1500

    QTimer.singleShot(splash_time, splash.close)
    QTimer.singleShot(splash_time, main_win.showMaximized)

    app.exec_()
    if main_win.results_frame.temp_file is not None:
        main_win.results_frame.temp_file.close()
