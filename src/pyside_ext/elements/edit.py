#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit

from src.common.constant import SettingsPanelSize
from src.common.decorators import log_method_noarg, log_method
from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.elements.utility.layout_helpers import empty_widget
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class LabeledLineEdit(BasePanelElement):
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
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight),

        self.edit_widget = QLineEdit(self.parent_widget)
        self.edit_widget.setMaximumWidth(SettingsPanelSize.max_col_width)
        self.edit_widget.setAlignment(Qt.AlignmentFlag.AlignLeft),

        set_stylesheet(
            self.edit_widget,
            css(
                border=Style.General.border,
                border_color=Style.Color.BorderElevated,
                background_color=Style.Color.BackgroundEdit,
            ),
        )
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.edit_widget)
        return self

    @log_method
    def set_editing_finished_handler(self, handler):
        self.edit_widget.editingFinished.connect(handler)

    @log_method_noarg
    def get_text(self):
        return self.edit_widget.text()

    @log_method
    def set_text(self, text: str):
        self.edit_widget.setText(text)
