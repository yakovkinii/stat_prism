import qtawesome as qta
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QListWidgetItem

from src.common import create_tool_button_qta
from src.common.registry import log_method
from src.core.common.column_selector.check_list.ui import CheckListWidget


class Filter:
    @log_method
    def __init__(self, parent, owner):
        self.owner = owner
        self.frame = QFrame(parent)

        self.AcceptButton = create_tool_button_qta(
            parent=self.frame,
            button_geometry=QtCore.QRect(10, 10, 181, 71),
            icon_path="fa5.check-circle",
            icon_size=QtCore.QSize(40, 40),
        )

        self.CancelButton = create_tool_button_qta(
            parent=self.frame,
            button_geometry=QtCore.QRect(10 + 380 - 181, 10, 181, 71),
            icon_path="fa5.times-circle",
            icon_size=QtCore.QSize(40, 40),
        )
        self.AcceptButton.pressed.connect(self.accept)
        self.CancelButton.pressed.connect(self.owner.column_selector_cancel)

        self.list_widget = CheckListWidget(self.frame)
        self.list_widget.setGeometry(QtCore.QRect(10, 100, 381, 973))
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    @log_method
    def configure(self, columns, dtypes, selected_columns, allowed_dtypes):
        while self.list_widget.count() > 0:
            self.list_widget.takeItem(0)

        numeric_icon = qta.icon("mdi.numeric")
        string_icon = qta.icon("mdi.alphabetical")

        icon_dict = {
            "int64": numeric_icon,
            "float64": numeric_icon,
            "object": string_icon,
        }

        for col, dtype in zip(columns, dtypes):
            item = QListWidgetItem(col)
            item.setIcon(icon_dict[dtype] if dtype in icon_dict else string_icon)
            self.list_widget.add_item_custom(item, checkable=dtype in allowed_dtypes, checked=col in selected_columns)

        self.list_widget.clearSelection()

    def accept(self):
        selected_columns = [
            self.list_widget.item(i).text()
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).checkState() == Qt.Checked
        ]
        self.owner.column_selector_accept(selected_columns)
