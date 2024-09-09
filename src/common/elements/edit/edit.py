from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit

from src.common.elements.base.base import BasePanelElement
from src.common.elements.utility.layout_helpers import empty_widget


class LabeledLineEdit(BasePanelElement):
    def __init__(self, label_text):
        super().__init__()
        self.label_text = label_text

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QHBoxLayout,
        )
        self.label = QLabel(self.label_text)
        self.edit_widget = QLineEdit(self.parent_widget)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.edit_widget)
