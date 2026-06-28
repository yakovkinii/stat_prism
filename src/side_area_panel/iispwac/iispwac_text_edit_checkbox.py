#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6.QtWidgets import QCheckBox, QLineEdit

from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.layout import VBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACLongTextEditCheckBox(ItemInSidePanelWithAutoConfig):
    def __init__(self, label_text: str, default_state: bool, default_from_column_selector: bool):
        super().__init__()
        self.label_text = label_text
        self.default_state = default_state
        self.handler_editing_finished = None
        self.default_from_column_selector = default_from_column_selector

    def post_init(self, name, parent_widget):
        self.name = name
        self.widget, self.layout = add_widget(
            parent=parent_widget,
            inner_layout_class=VBoxLayout,
            css=css(
                border=Style.General.border_elevated,
            ),
        )
        self.layout.setContentsMargins(5, 5, 5, 5),
        self.layout.setSpacing(2),
        self.checkbox, _ = add_widget(
            widget=QCheckBox(self.label_text, self.widget),
            outer_layout=self.layout,
        )
        self.checkbox.setChecked(self.default_state)
        self.checkbox.stateChanged.connect(self.on_editing_finished)

        self.edit, _ = add_widget(
            widget=QLineEdit(self.widget),
            outer_layout=self.layout,
        )
        self.clear_alert()
        self.edit.editingFinished.connect(self.on_editing_finished)
        self.edit.setEnabled(self.default_state)

    def get_kwargs(self):
        return {
            self.name: {
                "rename": self.checkbox.isChecked(),
                "new_name": self.edit.text(),
            }
        }

    def configure(self, **kwargs):
        config = kwargs[self.name]
        if config is None:
            if self.default_from_column_selector:
                config = {
                    "rename": self.default_state,
                    "new_name": self.get_default_name_from_kwargs(**kwargs),
                }
            else:
                config = {
                    "rename": self.default_state,
                    "new_name": "",
                }

        if config["new_name"] == "":
            config["new_name"] = self.get_default_name_from_kwargs(**kwargs)

        self.edit.setText(config["new_name"])
        self.checkbox.setChecked(config["rename"])
        self.edit.setEnabled(config["rename"])

    def get_default_name_from_kwargs(self, **kwargs) -> str:
        if not self.default_from_column_selector:
            return ""

        default = kwargs["column_selector"]
        new_name = ""
        try:
            new_name = default[0][0]
        except Exception:
            pass
        return new_name

    def set_alert(self):
        set_stylesheet(
            self.edit,
            css(
                border="1px solid red",
            ),
            css(
                "QLineEdit:disabled",
                background=Style.Color.BackgroundElevated,
            ),
        )

    def clear_alert(self):
        set_stylesheet(
            self.edit,
            css(
                border=Style.General.border_elevated,
            ),
            css(
                "QLineEdit:disabled",
                background=Style.Color.BackgroundElevated,
            ),
        )

    def on_editing_finished(self):
        if self.handler_editing_finished is not None:
            self.handler_editing_finished(self)
        self.on_recalculate()

    def set_handler_editing_finished(self, handler):
        self.handler_editing_finished = handler
