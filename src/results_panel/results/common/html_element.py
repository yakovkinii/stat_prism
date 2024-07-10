import logging
from typing import List, Union

from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QTextEdit, QTextBrowser

from src.common.unique_qss import set_stylesheet
from src.results_panel.results.common.base import BaseResultElement


class Cell:
    def __init__(
        self,
        text: str = "",
        is_bold: bool = False,
        is_italic: bool = False,
        border_left: bool = False,
        border_right: bool = False,
        border_top: bool = False,
        border_bottom: bool = False,
        col_span: int = 1,
        row_span: int = 1,
        push_to_right: bool = False,
        push_to_left: bool = False,
        center: bool = False,
        is_doubled: bool = False,
        no_wrap: bool = False,
    ):
        self.text = text
        self.is_bold = is_bold
        self.is_italic = is_italic
        self.border_left = border_left
        self.border_right = border_right
        self.border_top = border_top
        self.border_bottom = border_bottom
        self.col_span = col_span
        self.row_span = row_span
        self.push_to_right = push_to_right
        self.push_to_left = push_to_left
        self.center = center
        self.is_doubled = is_doubled
        self.no_wrap = no_wrap


class Row:
    def __init__(self, cells: List[Cell]):
        self.cells: List[Cell] = cells


class HTMLTable:
    def __init__(self, rows: List[Row], border_top: bool = True, border_bottom: bool = True):
        self.rows: List[Row] = rows
        self.border_top = border_top
        self.border_bottom = border_bottom
        self.table_id: str = ""
        self.table_caption: str = ""
        self.table_note: str = ""

    def get_html(self):
        # Caption
        html = ""
        html += f'<span class="double-spacing font"><b>Table {self.table_id}.</b></span> <br>'
        html += f'<span class="double-spacing font">{self.table_caption}</span><br><br>'

        style = ""
        if self.border_top:
            style += "border-top: 2px solid black;"
        if self.border_bottom:
            style += "border-bottom: 2px solid black;"

        html += f'<table style="{style}" class="font">'

        for row in self.rows:
            html += "<tr>"
            for cell in row.cells:
                style = "padding: 5px;"
                attributes = ""
                if cell.is_doubled:
                    style += "width: 40px;"
                else:
                    style += "width: 80px;"
                if cell.is_bold:
                    style += "font-weight: bold;"
                if cell.is_italic:
                    style += "font-style: italic;"
                if cell.border_left:
                    style += f"border-left: 1px solid black;"
                if cell.border_right:
                    style += f"border-right: 1px solid black;"
                if cell.border_top:
                    style += f"border-top: 1px solid black;"
                if cell.border_bottom:
                    style += f"border-bottom: 1px solid black;"
                if cell.col_span > 1:
                    attributes += f' colspan="{cell.col_span}"'
                if cell.row_span > 1:
                    attributes += f' rowspan="{cell.row_span}"'
                if cell.push_to_right:
                    style += "text-align: right; padding-right: 0px; margin-right:0px;"
                if cell.push_to_left:
                    style += "text-align: left; padding-left: 0px; margin-left:0px;"
                if cell.center:
                    style += "text-align: center;"
                if cell.no_wrap:
                    style += "white-space: nowrap;"
                html += f'<td style="{style}" {attributes}>{cell.text}</td>'
            html += "</tr>"
        html += "</table><br>"
        if self.table_note != "":
            html += f'<span class="double-spacing font"><i>Note.</i> {self.table_note}</span>'

        # print(html)
        return html

    def add_single_row_apa(self, row: Row):
        for cell in row.cells:
            cell.border_top = True
        self.rows.append(row)

    def add_multirow_apa(self, rows: List[Row]):
        for cell in rows[0].cells:
            cell.border_top = True
        for row in rows:
            self.rows.append(row)


class HTMLText:
    def __init__(self, text):
        self.text: str = text

    def get_html(self):
        return f'<span class="double-spacing font">{self.text}</span><br><br>'


class HTMLResultElement(BaseResultElement):
    def __init__(self, tab_title="HTML Result Element"):
        super().__init__()
        self.title: str = tab_title
        self.class_id: str = "HTMLResultElement"
        self.items: List[Union[HTMLTable, HTMLText]] = []


class HTMLResultElementWidgetContainer:
    def __init__(self, parent_widget, result_element: HTMLResultElement):
        self.result_element = result_element
        self.widget = QLabel(parent_widget)
        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(10, 10, 10, 10)

        self.webview = QWebEngineView(self.widget)
        self._html = self.get_html()
        logging.debug(f'setting html')
        self.webview.setHtml(self._html)
        logging.debug(f'setted html')
        self.widget_layout.addWidget(self.webview)
        logging.debug(f'added to layout')


    def get_html(self):
        html = "<HTML>"+STYLES
        html+="<br><br><br>".join([item.get_html() for item in self.result_element.items])
        html+="</HTML>"
        return html


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