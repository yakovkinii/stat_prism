#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

from PySide6.QtWidgets import QCheckBox

from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.size import Font
from src.common.unique_qss import set_stylesheet
from src.pyside_ext.styling import css, Style


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
                width="20px",
                height="20px",
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
