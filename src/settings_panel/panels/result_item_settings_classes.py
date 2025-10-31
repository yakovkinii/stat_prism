#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import Tuple

from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
)

from src.common.constant import SettingsPanelSize
from src.common.decorators import log_method_noarg
from src.common.messages import Message, MessageType
from src.common.qcolor import Colors
from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.elements.checkbox import LargeCheckbox
from src.pyside_ext.elements.edit import LabeledLineEdit
from src.pyside_ext.elements.utility.layout_helpers import (
    empty_widget,
    widget_in_layout,
)
from src.pyside_ext.markup import css
from src.pyside_ext.unique_qss import set_stylesheet


class ColorGridItemSetting(BasePanelElement):
    def __init__(self, current_color: Tuple[int, int, int], add_stretch=False):
        super().__init__()
        self.current_color = current_color
        self.add_stretch = add_stretch

    def get_current_value(self):
        return self.current_color

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [l.setContentsMargins(5, 0, 5, 0)],
        )
        initial: QColor = None
        self.selected_color = QColor(initial or QColor(255, 255, 255))
        self.selected_btn = None

        base_colors = Colors().colors

        # Grid of color buttons (4 rows x 7 cols)
        self.grid_widget, self.grid_layout = empty_widget(
            parent=self.widget,
            inner_layout_class=QGridLayout,
            outer_layout=self.layout,
            setup=lambda w, l: [
                l.setSpacing(4),
                l.setContentsMargins(2, 2, 2, 2),
            ],
        )

        for row in range(4):
            for col, (r, g, b) in enumerate(base_colors):
                # determine RGB variant per row
                if row == 0:
                    # raw: original
                    pr = 255 if r > 120 else 0
                    pg = 255 if g > 120 else 0
                    pb = 255 if b > 120 else 0
                    if (r, g, b) == (255, 100, 0):  # Exception for orange
                        pr, pg, pb = (255, 128, 0)

                elif row == 3:
                    # lighter: mix with white 50%
                    pr = int(r + (255 - r) * 0.5)
                    pg = int(g + (255 - g) * 0.5)
                    pb = int(b + (255 - b) * 0.5)
                elif row == 2:
                    # base: original (repeat raw)
                    pr, pg, pb = r, g, b
                else:
                    # darker: mix with black 40%
                    pr = int(r * 0.6)
                    pg = int(g * 0.6)
                    pb = int(b * 0.6)

                color = QtGui.QColor(pr, pg, pb)
                btn = QPushButton()
                # btn.setFixedSize(20, 30)
                btn.setFixedHeight(30)
                set_stylesheet(
                    btn,
                    css(
                        background_color=f"rgb({pr},{pg},{pb})",
                    ),
                )
                btn.clicked.connect(lambda _, b=btn, c=color: self._on_color_selected(b, c))
                self.grid_layout.addWidget(btn, row, col)

        if self.add_stretch:
            self.layout.addStretch()

    def _on_color_selected(self, btn: QPushButton, color: QColor):
        self.current_color = color.getRgb()[:3]
        self.handler(Message(MessageType.EDITING_FINISHED, payload=None, caller_id=self.element_id))


class SingleLineTextResultItemSetting(BasePanelElement):
    def __init__(self, label, current_value):
        super().__init__()

        self.label = label
        self.current_value = current_value
        # ---
        self.line_edit = None

    def get_current_value(self):
        return self.current_value

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
        )
        self.line_edit = LabeledLineEdit(label_text=self.label)
        self.line_edit.inject(self.widget, self.handler, self.element_id)
        self.line_edit.setup()
        self.line_edit.set_text(self.current_value)
        self.layout.addWidget(self.line_edit.widget)
        self.line_edit.set_editing_finished_handler(self.on_edit_finished)

    @log_method_noarg
    def on_edit_finished(self):
        self.current_value = self.line_edit.get_text()
        self.handler(Message(MessageType.EDITING_FINISHED, payload=None, caller_id=self.element_id))


class NumberCaptionResultItemSetting(BasePanelElement):
    def __init__(self, current_number, current_caption, add_stretch=False):
        super().__init__()
        self.number = SingleLineTextResultItemSetting("Number:", current_number)
        self.caption = SingleLineTextResultItemSetting("Caption:", current_caption)
        self.add_stretch = add_stretch

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda widget, layout: [
                layout.setContentsMargins(0, 5, 0, 5),
                layout.setSpacing(10),
            ],
        )

        self.number.inject(self.widget, self.handler, self.element_id)
        self.number.setup()
        self.layout.addWidget(self.number.widget)

        self.caption.inject(self.widget, self.handler, self.element_id)
        self.caption.setup()
        self.layout.addWidget(self.caption.widget)
        if self.add_stretch:
            self.layout.addStretch()

    def get_number(self):
        return self.number.current_value

    def get_caption(self):
        return self.caption.current_value


class ContainerResultItemSetting(BasePanelElement):
    def __init__(self, items, add_stretch=False):
        super().__init__()
        self.items = items
        self.add_stretch = add_stretch

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda widget, layout: [
                layout.setContentsMargins(0, 5, 0, 5),
                layout.setSpacing(10),
            ],
        )
        for item in self.items:
            item.inject(self.widget, self.handler, self.element_id)
            item.setup()
            self.layout.addWidget(item.widget)
        if self.add_stretch:
            self.layout.addStretch()


class SliderResultItemSetting(BasePanelElement):
    def __init__(self, label, current_value, min_value, max_value, step, add_stretch=False):
        super().__init__()
        self.label = label
        self.current_value = current_value
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        assert add_stretch is False, "Stretch is not supported for SliderResultItemSetting"
        self.add_stretch = add_stretch
        # ---
        self.slider = None

    def get_current_value(self):
        return self.current_value

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QHBoxLayout,
            setup=lambda widget, layout: [
                (
                    layout.setContentsMargins(5, 0, 5, 0),
                    layout.setSpacing(10),
                    layout.setStretch(1, 1),
                    layout.setStretch(0, 0),
                )
            ],
        )

        self.label_widget = widget_in_layout(
            widget=QLabel(self.label),
            layout=self.layout,
        )

        self.slider = widget_in_layout(
            widget=QSlider(Qt.Orientation.Horizontal),
            layout=self.layout,
            setup=lambda widget, layout: [
                widget.setMinimum(0),
                widget.setMaximum(int((self.max_value - self.min_value) / self.step)),
                widget.setValue(int((self.current_value - self.min_value) / self.step)),
                widget.valueChanged.connect(self.slider_value_changed),
                widget.setMaximumWidth(SettingsPanelSize.max_col_width),
            ],
        )

    def slider_value_changed(self, value):
        self.current_value = self.min_value + value * self.step
        self.handler(Message(MessageType.EDITING_FINISHED, payload=None, caller_id=self.element_id))


class CheckboxResultItemSetting(BasePanelElement):
    def __init__(self, label, current_value, add_stretch=False):
        super().__init__()
        self.label = label
        self.current_value = current_value
        assert add_stretch is False, "Stretch is not supported for CheckboxResultItemSetting"
        self.add_stretch = add_stretch
        # ---
        self.slider = None

    def get_current_value(self):
        return self.current_value

    def setup(self):
        self.large_checkbox = LargeCheckbox(label_text=self.label)
        self.large_checkbox.inject(self.parent_widget, self.handler, self.element_id)
        self.large_checkbox.setup()

        self.widget = self.large_checkbox.widget
        self.large_checkbox.widget.setChecked(self.current_value)
        self.large_checkbox.widget.stateChanged.connect(self.on_checkbox_state_changed)

    def on_checkbox_state_changed(self, state):
        self.current_value = state == Qt.CheckState.Checked.value
        self.handler(Message(MessageType.EDITING_FINISHED, payload=None, caller_id=self.element_id))
