from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt

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

    @log_method
    def resizeEvent(self, event):
        super().resizeEvent(event)
        scrollbar_height = self.horizontalScrollBar().height()
        min_height = self.widget().minimumSizeHint().height() + scrollbar_height
        self.setMinimumHeight(min_height)


class TableResultItemWidget:
    @log_method
    def __init__(self, parent, result_widget_instance, item: TableResultItem):
        html_table = item.dataframe.to_html(index=False)
        self.html_content = CSS_STYLE + f'<div class="scrollable">{html_table}</div>'

        self.result_widget_instance = result_widget_instance
        self.item: TableResultItem = item

        self.frame = QtWidgets.QFrame(parent)

        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setContentsMargins(20, 0, 20, 0)
        self.title_widget = TitleWidget(self.frame, self.item.title)
        self.gridLayout.addWidget(self.title_widget)
        self.label = LabelClickable(self.frame)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setText(self.html_content)
        self.label.adjustSize()

        self.scroll_area = ScrollAreaMinimumHeight(self.frame)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.gridLayout.addWidget(self.scroll_area)
