#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6.QtWidgets import QLabel, QLineEdit

from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.layout import VBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACLongTextEdit(ItemInSidePanelWithAutoConfig):
    def __init__(self, label_text: str):
        super().__init__()
        self.label_text = label_text
        self.handler_editing_finished = None

    def post_init(self, name, parent_widget):
        self.name = name
        self.widget, self.layout = add_widget(
            parent=parent_widget,
            inner_layout_class=VBoxLayout,
        )
        self.layout.setContentsMargins(2, 2, 2, 2),
        self.layout.setSpacing(5),
        self.label, _ = add_widget(
            widget=QLabel(self.label_text, self.widget),
            outer_layout=self.layout,
        )

        self.edit, _ = add_widget(
            widget=QLineEdit(self.widget),
            outer_layout=self.layout,
        )
        self.clear_alert()
        self.edit.editingFinished.connect(self.on_editing_finished)

    def get_kwargs(self):
        return {self.name: self.edit.text()}

    def configure(self, **kwargs):
        text = kwargs[self.name]
        self.edit.setText(text)

    def set_alert(self):
        set_stylesheet(
            self.edit,
            css(
                border="1px solid red",
            ),
        )

    def clear_alert(self):
        set_stylesheet(
            self.edit,
            css(
                border=Style.General.border_elevated,
            ),
        )

    def on_editing_finished(self):
        if self.handler_editing_finished is not None:
            self.handler_editing_finished(self)
        self.on_recalculate()

    def set_handler_editing_finished(self, handler):
        self.handler_editing_finished = handler
