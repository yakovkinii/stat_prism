import os
import tempfile

from PyQt5 import QtWebEngineWidgets, QtWidgets
from PyQt5.QtCore import QUrl


class Results:
    def __init__(self, parent):
        #   parent
        #       frame
        #           gridLayout
        #               scrollArea
        #                   scrollAreaWidgetContents
        #                       gridLayout_2
        #                           browser

        self.frame = QtWidgets.QFrame(parent)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QtWidgets.QScrollArea(self.frame)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)

        self.browser = QtWebEngineWidgets.QWebEngineView(self.scrollAreaWidgetContents)

        self.gridLayout_2.addWidget(self.browser)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea)
        self.temp_file = None

    def retranslateUI(self):
        pass

    def update_browser(self, output):
        if self.temp_file is not None:
            self.temp_file.close()
        self.temp_file = tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", delete=False, suffix=".html"
        )
        self.temp_file.write(output)
        self.temp_file.seek(0)
        self.browser.load(QUrl.fromLocalFile(os.path.abspath(self.temp_file.name)))
