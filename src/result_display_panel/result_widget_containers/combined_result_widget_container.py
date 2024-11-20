#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

import logging

from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout, QWidget

from src.common.constant import BASE_STYLES
from src.common.result.registry import RESULTS


class CombinedResultElementWidgetContainer:
    def __init__(self, parent_widget, result_id):
        self.result_id = result_id
        self.widget = QWidget(parent_widget)
        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)

        self.webview = QWebEngineView(self.widget)
        self._html = self.get_html()
        logging.debug(f"setting html")
        self.webview.setHtml(self._html)
        logging.debug(f"setted html")
        self.widget_layout.addWidget(self.webview)
        logging.debug(f"added to layout")

    def get_html(self):
        html = "<HTML>" + BASE_STYLES
        if self.result_id == -1:
            html += "<hr>".join([result.get_html() for result in RESULTS.values()])
        else:
            html += RESULTS[self.result_id].get_html()
        html += "</HTML>"
        # logging.info(html)
        return html

    def copy_for_word(self):
        logging.info("Copying for word")
        logging.info(self.get_html())

        self.webview.setFocus()
        self.webview.triggerPageAction(QWebEnginePage.WebAction.SelectAll)
        self.webview.triggerPageAction(QWebEnginePage.WebAction.Copy)
        self.webview.triggerPageAction(QWebEnginePage.WebAction.Unselect)
