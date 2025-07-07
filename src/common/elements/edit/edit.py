#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#
import logging

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit

from src.common.elements.base.base import BasePanelElement
from src.common.elements.utility.layout_helpers import empty_widget
from src.common.elements.utility.primitive_elements import EditableLabelWordwrap
from src.common.size import SettingsPanelSize
from src.common.unique_qss import set_stylesheet
from src.pyside_ext.styling import Style, css


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
        # self.label.setFixedWidth(SettingsPanelSize.col_width)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight),

        self.edit_widget = QLineEdit(self.parent_widget)
        self.edit_widget.setMaximumWidth(SettingsPanelSize.max_col_width)
        self.edit_widget.setAlignment(Qt.AlignmentFlag.AlignLeft),

        set_stylesheet(
            self.edit_widget,
            css(
                border="1px solid",
                border_color=Style.Color.Button,
                background_color=Style.Color.Base,
            )

        )
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.edit_widget)
        return self


class LabeledMultilineEdit(BasePanelElement):
    def __init__(self, label_text):
        super().__init__()
        logging.warning('LabeledMultilineEdit is deprecated')
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
        self.edit_widget = EditableLabelWordwrap(self.parent_widget)
        self.edit_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Fixed
        )
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.edit_widget)

    def sizeHint(self):
        return QtCore.QSize(20, self.calculate_height())

    def minimumSizeHint(self):
        return self.sizeHint()

    def calculate_height(self):
        # calculate height based on contents
        return self.edit_widget.height() + 20
