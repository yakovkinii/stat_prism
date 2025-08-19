#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6 import QtWidgets
from PySide6.QtWidgets import QHBoxLayout, QLabel

from src.common.messages import Message, MessageType
from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.elements.utility.layout_helpers import empty_widget


class Spin(BasePanelElement):
    def __init__(self, label_text, min_value, max_value):
        super().__init__()
        self.label_text = label_text
        self.min_value = min_value
        self.max_value = max_value

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

        self.spin_box = QtWidgets.QSpinBox(self.parent_widget)
        # self.spin_box.setMaximumWidth(20)
        self.spin_box.setRange(self.min_value, self.max_value)
        self.spin_box.valueChanged.connect(self.on_value_changed)
        self.layout.addWidget(self.spin_box)

    def on_value_changed(self):
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.spin_box.value(), caller_id=self.element_id))
