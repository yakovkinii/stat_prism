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


from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QDoubleSpinBox, QLabel

from src.common.decorators import log_method_noarg
from src.common.ui_constructor import create_simple_tool_button_qta
from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.layout import HBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACFloatSpin(ItemInSidePanelWithAutoConfig):
    """A plain, always-on float input: the counterpart of IISPWACSpin for non-integer values with a
    clean default (e.g. a smoothing multiplier that defaults to 1)."""

    def __init__(
        self,
        label_text: str,
        min_value: float,
        max_value: float,
        default_value: float = None,
        decimals: int = 2,
        step: float = 1.0,
        visible_when=None,
    ):
        super().__init__()
        self.label_text = label_text
        self.min_value = min_value
        self.max_value = max_value
        self.default_value = default_value if default_value is not None else min_value
        self.decimals = decimals
        self.step = step
        self.visible_when = visible_when
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

        # Larger, easier-to-hit step buttons flanking the field (mirrors IISPWACSpin).
        self.minus_button, _ = add_widget(
            widget=create_simple_tool_button_qta(parent=self.widget, icon_path="mdi6.minus", icon_size=QSize(20, 20)),
            outer_layout=self.layout,
        )
        self.minus_button.setFixedSize(QSize(28, 28))
        self.minus_button.setAutoRepeat(True)

        self.spin_box, _ = add_widget(
            widget=QDoubleSpinBox(self.widget),
            outer_layout=self.layout,
        )
        self.spin_box.setFixedWidth(60)
        self.spin_box.setRange(self.min_value, self.max_value)
        self.spin_box.setDecimals(self.decimals)
        self.spin_box.setSingleStep(self.step)
        self.spin_box.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_box.editingFinished.connect(self.on_value_changed)

        self.plus_button, _ = add_widget(
            widget=create_simple_tool_button_qta(parent=self.widget, icon_path="mdi6.plus", icon_size=QSize(20, 20)),
            outer_layout=self.layout,
        )
        self.plus_button.setFixedSize(QSize(28, 28))
        self.plus_button.setAutoRepeat(True)

        self.minus_button.clicked.connect(self.on_step_down)
        self.plus_button.clicked.connect(self.on_step_up)
        self.clear_alert()

    def get_kwargs(self):
        return {self.name: self.spin_box.value()}

    def configure(self, **kwargs):
        # Tolerate None and legacy blank/invalid strings (older saves used a text field) -> default.
        try:
            value = float(kwargs[self.name])
        except (TypeError, ValueError):
            value = float(self.default_value)
        self.spin_box.setValue(value)
        if self.visible_when is not None:
            self.widget.setVisible(bool(self.visible_when(kwargs)))

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

    @log_method_noarg
    def on_step_down(self):
        self.spin_box.stepDown()
        self.on_value_changed()

    @log_method_noarg
    def on_step_up(self):
        self.spin_box.stepUp()
        self.on_value_changed()

    def set_handler_value_changed(self, handler):
        self.handler_value_changed = handler
