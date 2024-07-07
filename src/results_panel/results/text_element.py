from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from src.results_panel.results.base_element import BaseResultElement


class TextResultElement(BaseResultElement):
    def __init__(self, text, title="Text Result Element"):
        super().__init__()
        self.title: str = title
        self.class_id: str = "TextResultElement"
        self.text = text


class TextResultElementWidgetContainer:
    def __init__(self, parent_widget, result_element: TextResultElement):
        self.result_element = result_element
        self.widget = QWidget(parent_widget)
        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(10, 10, 10, 10)

        self.label = QLabel(self.widget)
        self.label.setText(self.result_element.text)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.adjustSize()

        self.widget_layout.addWidget(self.label)
        self.widget_layout.addStretch()
