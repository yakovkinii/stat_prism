from PySide6.QtWidgets import QComboBox

from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType


class ComboBox(BasePanelElement):
    def setup(self):
        self.widget = QComboBox(self.parent_widget)
        self.widget.currentIndexChanged.connect(self.on_index_changed)

    def configure(self, items):
        self.widget.clear()
        self.widget.addItems(items)
        self.widget.setCurrentIndex(0)
        self.widget.currentTextChanged.connect(
            self.handler(Message(MessageType.STATE_CHANGED, payload=self.widget.currentIndex()))
        )

    def on_index_changed(self):
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.widget.currentIndex(), caller_id=self.element_id))
