#  Copyright (c) 2023 StatPrism Team. All rights reserved.



import qtawesome as qta
from PySide6 import QtWidgets
from PySide6.QtCore import QSize

from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class LargeButton(BasePanelElement):
    def __init__(self, label_text, icon_path):
        super().__init__()
        self.label = None
        self.widget = None

        self.label_text = label_text
        self.icon_path = icon_path if icon_path is not None else "msc.blank"

        self._margin = 20
        self._height = 81

    def setup(self):
        self.widget = QtWidgets.QPushButton(self.label_text)
        set_stylesheet(
            self.widget,
            css(
                margin_top="2px",
                font_family=Style.FontFamily.SegoeUI,
                font_size=Style.FontSize.larger,
                text_align="left",
                border=Style.General.border,
                border_color=Style.Color.BorderElevated,
            ),
            css(
                "#id:hover",
                border_color=Style.Color.Highlight,
            ),
        )
        icon = qta.icon(self.icon_path)
        self.widget.setIcon(icon)
        self.widget.setIconSize(QSize(60, 60))
        self.widget.setFixedHeight(70)
        self.widget.clicked.connect(self.clicked)

    def clicked(self):
        message = Message(message_type=MessageType.CLICKED, caller_id=self.element_id, payload=None)
        self.handler(message)
