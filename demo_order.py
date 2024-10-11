from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QListWidget,
                               QListWidgetItem, QPushButton, QLabel, QHBoxLayout)


class CustomListWidgetItem(QWidget):
    def __init__(self, text):
        super().__init__()
        layout = QHBoxLayout(self)
        self.label = QLabel(text)
        layout.addWidget(self.label)


class CustomListWidget(QListWidget):
    def __init__(self):
        super().__init__()

        # Enable drag and drop
        self.setDragDropMode(QListWidget.InternalMove)

        # Set selection mode to single
        self.setSelectionMode(QListWidget.SingleSelection)

    def add_custom_item(self, text):
        # Create QListWidgetItem
        item = QListWidgetItem(self)

        # Create custom widget for the list item
        custom_widget = CustomListWidgetItem(text)
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


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Main layout
        layout = QVBoxLayout(self)

        # Custom list widget
        self.list_widget = CustomListWidget()
        layout.addWidget(self.list_widget)

        # Add some initial items
        self.list_widget.add_custom_item("Item 1")
        self.list_widget.add_custom_item("Item 2")
        self.list_widget.add_custom_item("Item 3")
        self.list_widget.add_custom_item("Item 4")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
