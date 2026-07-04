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


from PySide6.QtWidgets import QCheckBox

from src.common.messages import Message, MessageType
from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class LargeCheckbox(BasePanelElement):
    def __init__(self, label_text):
        super().__init__()
        self.label_text = label_text

    def setup(self):
        self.widget = QCheckBox(self.parent_widget)
        self.widget.setText(self.label_text)
        self.widget.stateChanged.connect(
            lambda: self.handler(
                Message(message_type=MessageType.STATE_CHANGED, caller_id=self.element_id, payload=None)
            )
        )

        set_stylesheet(
            self.widget,
            css(
                font_family=Style.FontFamily.SegoeUI,
                font_size=Style.FontSize.regular,
            ),
            css(
                "#id::indicator",
                width=Style.General.checkbox_size_css,
                height=Style.General.checkbox_size_css,
            ),
            css(
                "#id::indicator:checked",
                image="url(:/mat/resources/checked.png)",
            ),
            css(
                "#id::indicator:unchecked",
                image="url(:/mat/resources/unchecked.png)",
            ),
            css(
                "#id::indicator:checked:disabled",
                image="url(:/mat/resources/checked_disabled.png)",
            ),
            css(
                "#id::indicator:unchecked:disabled",
                image="url(:/mat/resources/unchecked_disabled.png)",
            ),
        )
