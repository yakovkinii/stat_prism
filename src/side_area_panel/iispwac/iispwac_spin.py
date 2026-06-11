#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QLabel, QSpinBox

from src.common.decorators import log_method_noarg
from src.common.ui_constructor import create_simple_tool_button_qta
from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.layout import HBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACSpin(ItemInSidePanelWithAutoConfig):
    def __init__(self, label_text: str, min_value: int, max_value: int, default_value: int = None):
        super().__init__()
        self.label_text = label_text
        self.min_value = min_value
        self.max_value = max_value
        self.default_value = default_value if default_value is not None else min_value
        self.handler_value_changed = None

    def post_init(self, name, parent_widget):
        self.name = name

        self.widget, self.layout = add_widget(
            parent=parent_widget,
            inner_layout_class=HBoxLayout,
        )
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(5)

        self.label, _ = add_widget(
            widget=QLabel(self.label_text, self.widget),
            outer_layout=self.layout,
        )

        self.layout.addStretch()

        # Larger, easier-to-hit step buttons flanking the field (the native QSpinBox
        # arrows are tiny), with press-and-hold auto-repeat.
        self.minus_button, _ = add_widget(
            widget=create_simple_tool_button_qta(
                parent=self.widget, icon_path="mdi6.minus", icon_size=QSize(20, 20)
            ),
            outer_layout=self.layout,
        )
        self.minus_button.setFixedSize(QSize(28, 28))
        self.minus_button.setAutoRepeat(True)

        self.spin_box, _ = add_widget(
            widget=QSpinBox(self.widget),
            outer_layout=self.layout,
        )
        self.spin_box.setRange(self.min_value, self.max_value)
        self.spin_box.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_box.valueChanged.connect(self.on_value_changed)

        self.plus_button, _ = add_widget(
            widget=create_simple_tool_button_qta(
                parent=self.widget, icon_path="mdi6.plus", icon_size=QSize(20, 20)
            ),
            outer_layout=self.layout,
        )
        self.plus_button.setFixedSize(QSize(28, 28))
        self.plus_button.setAutoRepeat(True)

        self.minus_button.clicked.connect(self.spin_box.stepDown)
        self.plus_button.clicked.connect(self.spin_box.stepUp)
        self.clear_alert()

    def get_kwargs(self):
        return {self.name: self.spin_box.value()}

    def configure(self, **kwargs):
        value = kwargs[self.name]
        if value is None:
            value = self.default_value
        self.spin_box.setValue(value)

    @log_method_noarg
    def set_alert(self):
        set_stylesheet(self.spin_box, css(border="1px solid red"))

    @log_method_noarg
    def clear_alert(self):
        set_stylesheet(self.spin_box, css(border=Style.General.border_elevated))

    @log_method_noarg
    def on_value_changed(self):
        if self.handler_value_changed:
            self.handler_value_changed()
        self.on_recalculate()

    def set_handler_value_changed(self, handler):
        self.handler_value_changed = handler
