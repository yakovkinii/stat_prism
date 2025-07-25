#  Copyright (c) 2023 StatPrism Team. All rights reserved.



import logging
from typing import TYPE_CHECKING, Dict, Union

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QLabel

from src.common.constant import SettingsPanelSize
from src.common.debt import DEBTS, DebtType
from src.common.decorators import log_method, log_method_noarg
from src.common.elements.base.base import BasePanelElement
from src.common.elements.utility.layout_helpers import empty_widget
from src.common.elements.utility.primitive_elements import QWidgetClickable
from src.common.messages import Message
from src.common.ui_constructor import create_tool_button_qta
from src.pyside_ext.layout import HBoxLayout, VBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass
    from src.main_area_panel.ui_main_area import MainAreaClass


class MainAreaItem:
    def __init__(
        self,
        parent_widget,
        parent_class,
        root_class,
    ):
        # Setup
        self.study_index = None
        self.result_id: Union[int, None] = None
        self.caller_index = None
        self.configuring = False
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainAreaClass = parent_class
        self.gc_retainer = []
        self.full = True

        self.widget, self.layout = empty_widget(
            parent=parent_widget,
            inner_layout_class=HBoxLayout,
        )

        self.bar, _ = empty_widget(
            parent=self.widget,
            outer_layout=self.layout,
            widget_class=QWidgetClickable,
            setup=lambda w, l: [
                set_stylesheet(w, css(background_color=Style.Color.Background)),
                w.clicked.connect(self.toggle_full),
            ],
        )

        self.head_and_body, self.head_and_body_layout = empty_widget(
            parent=self.widget,
            inner_layout_class=VBoxLayout,
            outer_layout=self.layout,
        )

        self.head, self.head_layout = self.get_head()
        self.add_to_head()
        self.body, self.body_layout = self.get_body()
        self.add_to_body()

    def get_head(self):
        return empty_widget(
            parent=self.head_and_body,
            inner_layout_class=HBoxLayout,
            outer_layout=self.head_and_body_layout,
            setup=lambda w, l: [ set_stylesheet(w, css(background_color=Style.Color.Background))],
        )

    def add_to_head(self):
        placeholder_text = empty_widget(
            parent=self.head,
            outer_layout=self.head_layout,
            widget_class=QLabel,
            setup=lambda w, l: [
                w.setText("Placeholder"),
                set_stylesheet(w, css(font_size=Style.FontSize.regular)),
            ],
        )
        self.gc_retainer.append(placeholder_text)

    def get_body(self):
        return empty_widget(
            parent=self.head_and_body,
            inner_layout_class=HBoxLayout,
            outer_layout=self.head_and_body_layout,
            setup=lambda w, l: [ set_stylesheet(w, css(background_color="#aaa"))],
        )

    def add_to_body(self):
        ...

    def toggle_full(self):
        self.full = not self.full
        if self.full:
            self.body.show()
        else:
            self.body.hide()
        self.widget.update()
