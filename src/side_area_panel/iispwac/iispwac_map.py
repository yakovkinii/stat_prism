#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from abc import abstractmethod
from typing import List

from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel

from src.common.decorators import log_method_noarg
from src.common.messages import Message, MessageType
from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.elements.utility.layout_helpers import add_widget, empty_widget
from src.pyside_ext.layout import HBoxLayout, VBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACMap(ItemInSidePanelWithAutoConfig):
    def __init__(self, label_text: str, default_state: bool):
        super().__init__()
        self.label_text = label_text
        self.default_state = default_state
        self.handler_state_changed = None

    def post_init(self, name, parent_widget):
        self.name = name

        self.widget, self.layout = add_widget(
            parent=parent_widget,
            inner_layout_class=VBoxLayout,
        )
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.check, _ = add_widget(parent=self.widget, outer_layout=self.layout, widget=QCheckBox(parent_widget))
        self.check.setText(self.label_text)
        self.check.stateChanged.connect(self.on_state_changed)

        self.clear_alert()

    def get_kwargs(self):
        return {self.name: self.widget.isChecked()}

    def configure(self, **kwargs):
        state = kwargs[self.name]
        if state is None:
            state = self.default_state

        self.widget.setChecked(state)

    @log_method_noarg
    def set_alert(self):
        set_stylesheet(self.widget, css(border="1px solid red"))

    @log_method_noarg
    def clear_alert(self):
        # set color to checkbox itself
        set_stylesheet(self.widget, css(border="none"))

    @log_method_noarg
    def on_state_changed(self):
        if self.handler_state_changed:
            self.handler_state_changed()
        self.on_recalculate()

    def set_handler_state_changed(self, handler):
        self.handler_state_changed = handler
