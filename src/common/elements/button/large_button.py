from PySide6 import QtCore
from PySide6.QtWidgets import QWidget

from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.size import Font, SettingsPanelSize
from src.common.ui_constructor import create_label, create_tool_button_qta


class LargeButton(BasePanelElement):
    def __init__(self, label_text, icon_path):
        super().__init__()
        self.label = None
        self.button = None

        self.label_text = label_text
        self.icon_path = icon_path if icon_path is not None else "msc.blank"

        self._margin = 20
        self._height = 81

    def setup(self):
        self.widget = QWidget(self.parent_widget)

        self.widget.setFixedHeight(self._height + self._margin)

        self.button = create_tool_button_qta(
            parent=self.widget,
            button_geometry=QtCore.QRect(self._margin, self._margin, self._height, self._height),
            icon_path=self.icon_path,
            icon_size=QtCore.QSize(60, 60),
        )
        self.label = create_label(
            parent=self.widget,
            label_geometry=QtCore.QRect(120, self._margin, SettingsPanelSize.width - 120, self._height),
            font_size=Font.size_big,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter,
        )
        self.label.setText(self.label_text)

        self.button.clicked.connect(self.clicked)

    def clicked(self):
        message = Message(message_type=MessageType.CLICKED, caller_id=self.element_id, payload=None)
        self.handler(message)
