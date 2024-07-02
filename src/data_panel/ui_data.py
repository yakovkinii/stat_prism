import logging
from typing import TYPE_CHECKING

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout

from src.common.constant import DEBUG_LAYOUT
from src.common.decorators import log_method
from src.data_panel.header import LeftAlignHeaderView
from src.data_panel.model import DataModel
from src.data_panel.view import DataView

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class DataPanelClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        self.widget = QtWidgets.QWidget(parent_widget)
        self.widget.setContentsMargins(10, 0, 0, 0)
        self.widget.setStyleSheet("background-color: white;")

        if DEBUG_LAYOUT:
            self.widget.setStyleSheet("border: 1px solid blue; background-color: #eef;")
        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.widget_layout)

        # Definition
        self.tableview = DataView(self.widget)

        # Set the data model
        self.tabledata: DataModel = DataModel()
        self.tableview.setModel(self.tabledata)

        # self.tabledata = CustomTableWidget(self.widget)
        self.widget_layout.addWidget(self.tableview)

        self.tableview.setAutoFillBackground(False)
        self.tableview.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.tabledata.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        # self.tabledata.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tableview.setShowGrid(True)
        self.tableview.setGridStyle(QtCore.Qt.SolidLine)
        self.header = LeftAlignHeaderView(QtCore.Qt.Horizontal, self.tableview)
        self.tableview.setHorizontalHeader(self.header)

        self.tableview.horizontalHeader().setVisible(True)
        self.tableview.horizontalHeader().setCascadingSectionResizes(False)
        self.tableview.verticalHeader().setVisible(True)
        self.tableview.verticalHeader().setCascadingSectionResizes(False)
        self.tableview.verticalHeader().setHighlightSections(True)
        self.tableview.verticalHeader().setSortIndicatorShown(False)
        self.tableview.verticalHeader().setStretchLastSection(False)
        self.tableview.verticalHeader().setStyleSheet("background-color: white;")
        # self.tableview.horizontalHeader().setStyleSheet("background-color: rgb(240, 240, 250);")
        # set the background color of the vertical header items to 240, 240, 250
        # self.tableview.verticalHeader().setStyleSheet(
        #     "QHeaderView::section{background-color: rgb(240, 240, 250);}"
        # )
        # self.tableview.verticalHeader().setStyleSheet("background-color: rgb(240, 240, 250);")

        self.tableview.horizontalHeader().sectionClicked.connect(self.on_selection_changed)

    @log_method
    def on_selection_changed(
        self,
        selected,
    ):
        # This method will be called whenever the selection changes
        selected_columns = list({index.column() for index in self.tableview.selectedIndexes()})

        if len(selected_columns) == 1:
            self.root_class.action_activate_column_panel(selected_columns[0])
        elif len(selected_columns) > 1:
            self.root_class.action_activate_columns_panel(selected_columns)

        logging.debug(f"Selected columns: {selected_columns}")

    def retranslateUI(self):
        pass
