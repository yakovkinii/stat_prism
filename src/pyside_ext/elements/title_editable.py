#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.

# VALIDATED

from PySide6 import QtCore

from src.common.messages import Message, MessageType
from src.common.ui_constructor import create_label_editable_wordwrap
from src.pyside_ext.elements.base import BasePanelElement


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
