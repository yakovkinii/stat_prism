#  Copyright (c) 2023 StatPrism Team. All rights reserved.



from typing import Union, cast

from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QWidget

from src.common.elements.base.base import BasePanelElement


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
        layout.addWidget(self.label)


class CustomListWidget(QListWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # Enable drag and drop
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)

        # Set selection mode to single
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

    def add_custom_item(self, value, text):
        # Create QListWidgetItem
        item = QListWidgetItem(self)

        # Create custom widget for the list item
        custom_widget = CustomListWidgetItem(value, text)
        item.setSizeHint(custom_widget.sizeHint())

        # Add the custom widget into the list
        self.setItemWidget(item, custom_widget)

    def move_up(self, item):
        current_row = self.row(item)
        if current_row > 0:
            # Remove and reinsert at one row above
            self.takeItem(current_row)
            self.insertItem(current_row - 1, item)
            self.setCurrentRow(current_row - 1)

    def move_down(self, item):
        current_row = self.row(item)
        if current_row < self.count() - 1:
            # Remove and reinsert at one row below
            self.takeItem(current_row)
            self.insertItem(current_row + 1, item)
            self.setCurrentRow(current_row + 1)

    def minimumSizeHint(self):
        return self.sizeHint()
