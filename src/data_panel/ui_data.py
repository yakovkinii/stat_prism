import logging
from typing import TYPE_CHECKING

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QMessageBox, QVBoxLayout

from src.common.constant import DEBUG_LAYOUT
from src.common.decorators import log_method, log_method_noarg
from src.common.unique_qss import set_stylesheet
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
        set_stylesheet(self.widget, "#id{background-color: white;}")

        if DEBUG_LAYOUT:
            set_stylesheet(self.widget, "#id{border: 1px solid blue; background-color: #eef;}")
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
        self.tableview.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        # self.tabledata.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        # self.tabledata.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tableview.setShowGrid(True)
        self.tableview.setGridStyle(QtCore.Qt.PenStyle.SolidLine)
        self.header = LeftAlignHeaderView(QtCore.Qt.Orientation.Horizontal, self.tableview)
        self.tableview.setHorizontalHeader(self.header)

        # make table editable
        self.tableview.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)

        self.tableview.horizontalHeader().setVisible(True)
        self.tableview.horizontalHeader().setCascadingSectionResizes(False)
        self.tableview.verticalHeader().setVisible(True)
        self.tableview.verticalHeader().setCascadingSectionResizes(False)
        self.tableview.verticalHeader().setHighlightSections(True)
        self.tableview.verticalHeader().setSortIndicatorShown(False)
        self.tableview.verticalHeader().setStretchLastSection(False)
        set_stylesheet(
            self.tableview,
            "#id{outline:0;}"
            "#id>QHeaderView{background-color: white;}"
            "#id::item:selected:focus { background:#eee;}"  # Required for outline:0
            "#id::item:!selected:focus { background:transparent; }",  # Required for outline:0
        )

        self.tableview.verticalHeader().setHighlightSections(False)

        self.header.mouse_up.connect(self.on_selection_changed)
        # self.header.clicked.connect(self.on_selection_changed)
        # self.tableview.selectionModel().selectionChanged.connect(self.on_selection_changed)
        # self.header.
        self.header.edit_column_name.connect(self.on_selection_double_clicked)
        self.tableview.copy_signal.connect(self.copy_selection)
        self.tableview.paste_signal.connect(self.paste_selection)

    @log_method
    def on_selection_changed(self, *args, **kwargs):
        # This method will be called whenever the selection changes
        selected_columns = list({index.column() for index in self.tableview.selectedIndexes()})

        if len(selected_columns) == 1:
            self.root_class.action_activate_column_panel(selected_columns[0])
        elif len(selected_columns) > 1:
            self.root_class.action_activate_columns_panel(selected_columns)

        logging.debug(f"Selected columns: {selected_columns}")

    def retranslateUI(self):
        pass

    # function for copying selected table cells to clipboard
    @log_method_noarg
    def copy_selection(self):
        selected_indexes = self.tableview.selectedIndexes()
        if not selected_indexes:
            return
        selected_rows = list({index.row() for index in selected_indexes})
        selected_columns = list({index.column() for index in selected_indexes})
        selected_rows.sort()
        selected_columns.sort()
        selected_rows = [str(row) for row in selected_rows]
        selected_columns = [str(column) for column in selected_columns]
        copied_text = ""
        # if all rows selected
        if len(selected_rows) == self.tabledata.rowCount():
            selected_column_names = [self.tabledata.get_column_name(int(column)) for column in selected_columns]
            copied_text = "\t".join(selected_column_names) + "\n"

        data = self.tabledata.get_data()
        for row in selected_rows:
            for column in selected_columns:
                copied_text += str(data.iloc[int(row), int(column)]) + "\t"
            copied_text = copied_text[:-1] + "\n"
        QtWidgets.QApplication.clipboard().setText(copied_text)
        logging.info("Table copied to clipboard")

    @log_method_noarg
    def paste_selection(self):
        # QtWidgets.QApplication.clipboard().
        # retrieve the text from clipboard
        copied_text = QtWidgets.QApplication.clipboard().text()
        logging.debug(copied_text)
        # split the text into rows
        rows = copied_text.split("\n")
        if rows[-1] == "":
            rows = rows[:-1]

        # count cells in each row
        row_lengths = [len(row.split("\t")) for row in rows]
        # if all rows have the same number of cells
        if len(set(row_lengths)) != 1:
            logging.warning("Cannot paste table from clipboard. Rows have different number of cells")
            return

        # get the selected cells
        selected_indexes = self.tableview.selectedIndexes()
        if not selected_indexes:
            return

        selected_rows = list({index.row() for index in selected_indexes})
        selected_columns = list({index.column() for index in selected_indexes})

        # Validate selection size
        if len(selected_rows) != 1 or len(selected_columns) != 1:
            logging.warning("Cannot paste table from clipboard. Please select a single cell")
            QMessageBox.information(self.widget, "Cannot paste table", "Please select a single destination cell.")
            return

        selected_row = selected_rows[0]
        selected_column = selected_columns[0]
        logging.debug(f"Selected cell: {selected_row}, {selected_column}")
        # Check that there is enough space to paste
        if selected_row + len(rows) > self.tabledata.rowCount():
            logging.warning("Cannot paste table from clipboard. Not enough rows to paste")
            QMessageBox.information(self.widget, "Cannot paste table", "Not enough rows to paste the table.")
            return
        if selected_column + row_lengths[0] > self.tabledata.columnCount():
            logging.warning("Cannot paste table from clipboard. Not enough columns to paste")
            QMessageBox.information(self.widget, "Cannot paste table", "Not enough columns to paste the table.")
            return
        self.tabledata.beginResetModel()

        # iterate over the rows
        for row_index, row in enumerate(rows):
            # split the cells
            cells = row.split("\t")
            # iterate over the cells
            for column_index, cell in enumerate(cells):
                self.tabledata.setItem(selected_row + row_index, selected_column + column_index, cell)
        self.tabledata.endResetModel()
        logging.info("Table pasted from clipboard")

    @log_method
    def on_selection_double_clicked(self, column):
        logging.info(f"Double clicked column: {column}")
        self.root_class.action_current_column_begin_edit_title()
