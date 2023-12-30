import logging
from typing import TYPE_CHECKING, Dict

from PyQt5 import QtCore, QtWebEngineWidgets, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent

from core.constants import NO_RESULT_SELECTED, OUTPUT_WIDTH
from core.shared import result_container
from core.utility import get_html_start_end, log_method_noarg

if TYPE_CHECKING:
    from core.mainwindow.ui import MainWindow


class Browser(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, parent, results_instance, index):
        logging.info(f"init {index}")
        super().__init__(parent)

        self.results_instance: Results = results_instance
        self.setMinimumWidth(OUTPUT_WIDTH)
        self.html = None
        self.index = index
        self.loadFinished.connect(self.trigger_update_height)

    def trigger_update_height(self):
        logging.info(f"trigger update {self.index}")
        self.page().runJavaScript(
            "document.body.scrollHeight;", lambda height: self.update_height(height)
        )

    def update_height(self, height):
        if type(height) == int:
            logging.info(f"update height {self.index} to h={height} + 20")
            self.setMinimumHeight(height + 20)
            if result_container.current_result != NO_RESULT_SELECTED:
                logging.info("Triggering scroll")
                self.results_instance.scrollArea.ensureWidgetVisible(
                    self.results_instance.browsers[result_container.current_result]
                )
        else:
            logging.warning(f"non-int height type:" + str(height))

    def load_html(self, html):
        logging.info(f"load html {self.index}")
        self.html = html
        self.setHtml(self.html)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.trigger_update_height()

    def wheelEvent(self, event):
        # Propagate the event to the parent
        self.results_instance.scrollArea.wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            print("Left mouse button pressed in the web view")
            # Your custom action here

        # Call the base class implementation to ensure standard behavior
        super().mousePressEvent(event)


class Results:
    def __init__(self, parent, mainwindow_instance):
        #   parent
        #       frame
        #           gridLayout
        #               scrollArea
        #                   scrollAreaWidgetContents
        #                       gridLayout_2
        #                           browser
        self.mainwindow_instance: MainWindow = mainwindow_instance

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
        self.browsers: Dict[int, Browser] = dict()
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea)
        self.temp_file = None

        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def retranslateUI(self):
        pass

    @log_method_noarg
    def update(self):
        html_start, html_end = get_html_start_end()

        browsers_to_remove = set(self.browsers.keys()) - set(
            result_container.results.keys()
        )
        for result_id in browsers_to_remove:
            logging.info(f"Removing result {result_id} browser")
            del self.browsers[result_id]

        browsers_to_add = set(result_container.results.keys()) - set(
            self.browsers.keys()
        )
        for result_id in browsers_to_add:
            logging.info(f"Adding result {result_id} browser")
            html = html_start + result_container.results[result_id].content + html_end
            browser = Browser(self.scrollAreaWidgetContents, self, result_id)
            browser.load_html(html)
            self.browsers[result_id] = browser

        browsers_to_update = set(result_container.results.keys()) - browsers_to_add
        for result_id in browsers_to_update:
            html = html_start + result_container.results[result_id].content + html_end
            self.browsers[result_id].load_html(html)

        if len(browsers_to_add) != 0 or len(browsers_to_remove) != 0:
            logging.info("recreating the layout")
            # Clear layout
            for i in range(self.gridLayout_2.count()):
                self.gridLayout_2.takeAt(0)

            for result_id, result in result_container.results.items():
                self.gridLayout_2.addWidget(self.browsers[result_id])

        self.scrollArea.ensureWidgetVisible(
            self.browsers[result_container.current_result]
        )
