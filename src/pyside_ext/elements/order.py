#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.


from typing import Union, cast

from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QWidget

from src.pyside_ext.elements.base import BasePanelElement


class OrderVisualizer(BasePanelElement):
    def __init__(self):
        super().__init__()
        self.children = []
        self.layout_for_values = None

    def setup(self):
        self.widget = CustomListWidget(self.parent_widget)

    def configure(self, values):
        self.widget.clear()
        for value in values:
            self.widget.add_custom_item(value, str(value))

    def get_order_dict(self):
        order_dict = {}
        for i in range(self.widget.count()):
            item = self.widget.item(i)
            widget = cast(CustomListWidgetItem, self.widget.itemWidget(item))
            order_dict[widget.value] = i + 1
        return order_dict


class CustomListWidgetItem(QWidget):
    def __init__(self, value, text):
        super().__init__()
        self.value: Union[int, float, str] = value
        layout = QHBoxLayout(self)
        self.label = QLabel(text)
        # Tooltip shows the full value so it stays readable when the row is truncated.
        self.label.setToolTip(text)
        self.setToolTip(text)
        layout.addWidget(self.label)


class CustomListWidget(QListWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

    def add_custom_item(self, value, text):
        item = QListWidgetItem(self)

        custom_widget = CustomListWidgetItem(value, text)
        item.setSizeHint(custom_widget.sizeHint())

        self.setItemWidget(item, custom_widget)

    def move_up(self, item):
        current_row = self.row(item)
        if current_row > 0:
            self.takeItem(current_row)
            self.insertItem(current_row - 1, item)
            self.setCurrentRow(current_row - 1)

    def move_down(self, item):
        current_row = self.row(item)
        if current_row < self.count() - 1:
            self.takeItem(current_row)
            self.insertItem(current_row + 1, item)
            self.setCurrentRow(current_row + 1)

    def minimumSizeHint(self):
        return self.sizeHint()
