import os
import tempfile

from PyQt5 import QtWebEngineWidgets, QtWidgets
from PyQt5.QtCore import QUrl

from core.constants import OUTPUT_WIDTH
from core.shared import result_container
from core.utility import log_method_noarg, get_html_start_end


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

        # self.browser = QtWebEngineWidgets.QWebEngineView(self.scrollAreaWidgetContents)
        # self.browser.setMinimumWidth(OUTPUT_WIDTH)
        #
        # self.gridLayout_2.addWidget(self.browser)
        self.browsers = []
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea)
        self.temp_file = None

    def retranslateUI(self):
        pass

    @log_method_noarg
    def update(self):
        html_start, html_end = get_html_start_end()
        # Clear layout

        for i in range(self.gridLayout_2.count()):
            self.gridLayout_2.takeAt(0)

        self.browsers = dict()
        for result_id, result in result_container.results.items():
            html = html_start+result.content+html_end

            browser = QtWebEngineWidgets.QWebEngineView(self.scrollAreaWidgetContents)

            def update_size():
                browser.setMinimumWidth(OUTPUT_WIDTH)

                def update_height(height):
                    browser.setMinimumHeight(height)

                browser.page().runJavaScript(
                    "document.body.scrollHeight;",
                    lambda height: update_height(height)
                )

            if self.temp_file is not None:
                self.temp_file.close()
            self.temp_file = tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", delete=False, suffix=".html"
            )
            self.temp_file.write(html)
            self.temp_file.seek(0)
            browser.load(QUrl.fromLocalFile(os.path.abspath(self.temp_file.name)))
            browser.loadFinished.connect(update_size)
            self.gridLayout_2.addWidget(browser)
