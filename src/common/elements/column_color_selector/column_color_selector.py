#  Copyright (c) 2023 StatPrism Team. All rights reserved.



from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QGridLayout, QWidget

from src.common.constant import COLORS
from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.pyside_ext.markup import css
from src.pyside_ext.unique_qss import set_stylesheet


class ColumnColorSelector(BasePanelElement):
    def __init__(self):
        super().__init__()
        self.layout = None
        self.buttons = []

    def get_handler(self, index):
        message = Message(message_type=MessageType.CLICKED, caller_id=self.element_id, payload=index)
        return lambda: self.handler(message)

    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.layout = QGridLayout(self.widget)

        for i, color in enumerate(COLORS):
            button = QtWidgets.QToolButton(self.widget)
            button.setFixedWidth(35)
            button.setFixedHeight(35)
            button.setText("")
            set_stylesheet(
                button,
                css(background_color=str(color)),
            )
            button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
            self.buttons.append(button)
            self.layout.addWidget(button, i // 6, i % 6)
            button.clicked.connect(self.get_handler(i))
