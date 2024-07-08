import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.results_panel.results.common.base import BaseResultElement, APA_TABLE_STYLE_CLASSES


class DescriptiveTableResultElement(BaseResultElement):
    def __init__(self, dataframe, title="Table Result Element"):
        super().__init__()
        self.title: str = title
        self.class_id: str = "DescriptiveTableResultElement"

        self.dataframe = dataframe


class DescriptiveTableResultElementWidgetContainer:
    def __init__(self, parent_widget, result_element: DescriptiveTableResultElement):
        self.result_element = result_element
        self.widget = QWidget(parent_widget)
        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(10, 10, 10, 10)

        self.label = QLabel(self.widget)

        html = self.get_html()
        self.label.setText(html)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.adjustSize()

        self.widget_layout.addWidget(self.label)
        self.widget_layout.addStretch()

    def get_html(self):
        if self.result_element.dataframe is None:
            return ""

        df = self.result_element.dataframe

        html = "<table>"
        html += "<tr>"
        for column in df.columns:
            html += f'<td><span>{column}</span></td>'
        html += "</tr>"

        for i, row in df.iterrows():
            html += "<tr>"
            for j, (column, value) in enumerate(row.items()):
                if j == 0:  # Row header
                    html += f'<td><span style="background-color:transparent">{value}</span></td>'

                else:
                    html += f'<td>'
                    html += f'<span>{value}</span'
                    html += "</td>"
            html += "</tr>"
        html += "</table>"

        # html_table = self.item.dataframe.to_html(index=False)
        html = APA_TABLE_STYLE_CLASSES + f'<div class="scrollable">{html}</div>'

        return html

