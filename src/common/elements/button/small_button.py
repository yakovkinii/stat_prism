import qtawesome as qta
from PySide6 import QtWidgets
from PySide6.QtCore import QSize

from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.size import Font
from src.common.unique_qss import set_stylesheet


class SmallButton(BasePanelElement):
    def __init__(self, label_text, icon_path):
        super().__init__()
        self.label = None
        self.button = None

        self.label_text = label_text
        self.icon_path = icon_path if icon_path is not None else "msc.blank"

        self._margin_left = 0
        self._margin = 0
        self._height = 41

    def setup(self):
        self.widget = QtWidgets.QPushButton(self.label_text)
        set_stylesheet(
            self.widget,
            "#id{"
            "margin-top: 2px;"
            "font-family: Segoe UI;"
            "background-color: rgba(255,255,255, 50);"
            f"font-size: {Font.size}pt;"
            # align left
            "text-align: left;"
            "border: 1px solid #ddd;"
            "}"
            "#id:hover{"
            "background-color: rgb(229,241,251);"
            "border: 1px solid rgb(0,120,215)"
            "}",
        )
        icon = qta.icon(self.icon_path)
        self.widget.setIcon(icon)
        self.widget.setIconSize(QSize(40, 40))
        self.widget.setFixedHeight(50)
        self.widget.clicked.connect(self.clicked)

    def clicked(self):
        message = Message(message_type=MessageType.CLICKED, caller_id=self.element_id, payload=None)
        self.handler(message)
