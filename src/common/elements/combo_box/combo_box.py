#  Copyright (c) 2023 StatPrism Team. All rights reserved.



from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel

from src.common.elements.base.base import BasePanelElement
from src.common.elements.utility.layout_helpers import empty_widget
from src.common.messages import Message, MessageType


class ComboBox(BasePanelElement):
    def __init__(self, label_text):
        super().__init__()
        self.label_text = label_text

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QHBoxLayout,
            setup=lambda widget, layout: [
                layout.setContentsMargins(2, 2, 2, 2),
                layout.setSpacing(5),
            ],
        )

        self.label = QLabel(self.label_text)
        self.layout.addWidget(self.label)

        self.combo_box = QComboBox(self.parent_widget)
        self.combo_box.currentIndexChanged.connect(self.on_index_changed)
        self.layout.addWidget(self.combo_box)

    def configure(self, items):
        self.combo_box.clear()
        self.combo_box.addItems(items)
        self.combo_box.setCurrentIndex(0)
        self.combo_box.currentTextChanged.connect(
            self.handler(
                Message(
                    MessageType.STATE_CHANGED,
                    payload=self.combo_box.currentIndex(),
                    caller_id=self.element_id,
                )
            )
        )

    def on_index_changed(self):
        self.handler(
            Message(MessageType.STATE_CHANGED, payload=self.combo_box.currentIndex(), caller_id=self.element_id)
        )
