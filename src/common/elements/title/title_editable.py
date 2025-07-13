#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#

from PySide6 import QtCore

from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.ui_constructor import create_label_editable_wordwrap


class ColumnNameEditable(BasePanelElement):
    def __init__(self, label_text):
        super().__init__()
        self.label_text = label_text

    def setup(self):
        self.widget = create_label_editable_wordwrap(
            parent=self.parent_widget,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter,
        )
        self.widget.setText(self.label_text)
        self.widget.editingFinished.connect(self.editing_finished_handler)

    def editing_finished_handler(self):
        message = Message(message_type=MessageType.EDITING_FINISHED, caller_id=self.element_id, payload=True)
        self.handler(message)
