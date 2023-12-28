import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen
from ui.handlers.mainwindow_handler import MainWindowHandler
from yatools import logging_config

if __name__ == "__main__":
    logging_config.init()
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
    mainwin = MainWindowHandler()

    QTimer.singleShot(1500, splash.close)
    QTimer.singleShot(1500, mainwin.showMaximized)

    app.exec_()
    if mainwin.temp_file is not None:
        mainwin.temp_file.close()
