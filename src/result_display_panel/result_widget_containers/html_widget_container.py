import logging

from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout, QWidget

from src.common.result.classes.html_result import HTMLResultElement


class HTMLResultElementWidgetContainer:
    def __init__(self, parent_widget, result_element: HTMLResultElement):
        self.result_element = result_element
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
        html = "<HTML>" + STYLES
        html += "<br><br><br>".join([item.get_html() for item in self.result_element.items])
        html += "</HTML>"
        logging.info(html)
        return html

    def copy_for_word(self):
        logging.info("Copying for word")
        logging.info(self.get_html())

        self.webview.setFocus()
        self.webview.triggerPageAction(QWebEnginePage.WebAction.SelectAll)
        self.webview.triggerPageAction(QWebEnginePage.WebAction.Copy)
        self.webview.triggerPageAction(QWebEnginePage.WebAction.Unselect)


STYLES = (
    "<style>"
    ".double-spacing{"
    "line-height: 2;"
    "}"
    ".font {"
    "font-size: 12pt;"
    "font-family: 'Times New Roman';"
    "}"
    "table, th, td, span {"
    "border-collapse: collapse;"
    "font-size: 12pt;"
    "}"
    "</style>"
)
