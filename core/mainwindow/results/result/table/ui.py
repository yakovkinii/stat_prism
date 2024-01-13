import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import QApplication

from core.mainwindow.layout import VerticalLayout
from core.mainwindow.results.result.common.label import LabelClickable
from core.mainwindow.results.result.common.title import TitleWidget
from core.mainwindow.results.result.table.constant import CSS_STYLE
from core.objects import TableResultItem
from core.utility import log_method


class ScrollAreaMinimumHeight(QtWidgets.QScrollArea):
    @log_method
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

    def sizeHint(self) -> QtCore.QSize:
        width=super().sizeHint().width()
        scrollbar_height = self.horizontalScrollBar().height()
        return QSize(width,self.widget().sizeHint().height() + scrollbar_height + 5)


class TableResultItemWidget:
    @log_method
    def __init__(self, parent, result_widget_instance, item: TableResultItem):
        self.result_widget_instance = result_widget_instance
        self.item: TableResultItem = item
        self.html_content = self.get_html()

        self.frame = QtWidgets.QFrame(parent)

        self.layout = VerticalLayout(self.frame, padding_left=20, padding_right=20)

        self.title_widget = TitleWidget(self.frame, self.item.title)
        self.title_widget.setFixedWidth(999999)
        self.title_widget.adjustSize()

        self.layout.addWidget(self.title_widget)

        self.scroll_area = ScrollAreaMinimumHeight(self.frame)
        self.scroll_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Preferred)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)

        self.label = LabelClickable(self.scroll_area)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setText(self.html_content)
        self.label.adjustSize()

        self.scroll_area.setWidget(self.label)

        self.layout.addWidget(self.scroll_area)

    def get_html(self):
        if self.item.html is not None:
            return CSS_STYLE + f'<div class="scrollable">{self.item.html}</div>'
        df = self.item.dataframe
        if self.item.draw_index:
            df = df.reset_index()

        min_max = {
            col: [df[col].min(), df[col].max()]
            for col in df.columns
            if np.issubdtype(df[col].dtype, np.number)
        }

        df_non_numeric = df[
            [col for col in list(df.columns) if col not in min_max.keys()]
        ]

        category = {
            col: df_non_numeric[[col]]
            .drop_duplicates()
            .reset_index()
            .set_index(col)
            .rename(columns={"index": "id"})
            for col in df_non_numeric.columns
            if df_non_numeric[col].nunique() < 5
        }

        header_style = '"font-weight:500;background-color:rgba(0,0,0,10)"'

        html = "<table>"
        html += "<tr>"
        for column in df.columns:
            html += f'<td style={header_style}><span style="background-color:transparent">{column}</span></td>'
        html += "</tr>"

        for i, row in df.iterrows():
            html += "<tr>"
            for j, (column, value) in enumerate(row.items()):
                if j == 0:  # Row header
                    html += f'<td style={header_style}><span style="background-color:transparent">{value}</span></td>'

                else:
                    if column in min_max.keys():
                        color = self.color_for_value(
                            value, min_max[column][0], min_max[column][1]
                        )
                    elif column in category.keys():
                        color = self.color_for_category(category[value])
                    else:
                        color = "rgba(128,0,128,20)"
                    if not self.item.color_values:
                        color = "rgba(0,0,255,10)"
                    html += f'<td style="background-color: {color};">'
                    html += (
                        f'<span style = "background-color: transparent">{value}</span'
                    )
                    html += "</td>"
            html += "</tr>"
        html += "</table>"

        # html_table = self.item.dataframe.to_html(index=False)
        html = CSS_STYLE + f'<div class="scrollable">{html}</div>'


        return html

    @staticmethod
    def color_for_value(value, min_value, max_value):
        if min_value == max_value:
            return "rgba(128,0,128,20)"
        intensity = int(255 * (value - min_value) / (max_value - min_value))
        return f"rgba({intensity}, 0, {255-intensity}, 20)"

    @staticmethod
    def color_for_category(id):
        colors = {
            "0": "rgba(255, 0, 0, 20)",
            "1": "rgba(0, 128, 0, 20)",
            "2": "rgba(0, 0, 255, 20)",
            "3": "rgba(255, 165, 0, 20)",
            "4": "rgba(128, 0, 128, 20)",
        }
        return colors[id]
