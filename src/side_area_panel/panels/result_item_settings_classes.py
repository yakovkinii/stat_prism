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


from typing import Tuple

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProxyStyle,
    QPushButton,
    QSlider,
    QStyle,
    QVBoxLayout,
)

from src.common.constant import SettingsPanelSize
from src.common.decorators import log_method_noarg
from src.common.messages import Message, MessageType
from src.common.qcolor import Colors
from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.elements.checkbox import LargeCheckbox
from src.pyside_ext.elements.edit import LabeledLineEdit
from src.pyside_ext.elements.utility.layout_helpers import empty_widget, widget_in_layout
from src.pyside_ext.elements.utility.primitive_elements import NoScrollComboBox
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class _AbsoluteSliderStyle(QProxyStyle):
    # Makes a left-click anywhere on the groove jump the handle straight to the clicked position,
    # instead of Qt's default single page-step jump (which, on the short ranges these sliders use,
    # lurches almost from min to max on one click). Dragging is unaffected.
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.StyleHint.SH_Slider_AbsoluteSetButtons:
            return Qt.MouseButton.LeftButton.value
        return super().styleHint(hint, option, widget, returnData)


# Default-value tracking for settings that hold a single current_value. Subclasses must set
# self.default_value in __init__ (to the initial value).
class _ValueDefaultsMixin:
    def get_default_value(self):
        return self.default_value

    def set_default_value(self, value):
        self.default_value = value

    def restore_default_value(self):
        self.current_value = self.default_value

    def is_modified(self):
        return self.current_value != self.default_value


class ColorGridItemSetting(BasePanelElement):
    def __init__(self, current_color: Tuple[int, int, int], add_stretch=False, label: str = None):
        super().__init__()
        self.current_color = current_color
        self.default_color = current_color
        self.add_stretch = add_stretch
        self.label = label
        # ---
        self.color_button = None
        self._popup = None

    def get_current_value(self):
        return self.current_color

    def set_up_from_other_instance(self, other: "ColorGridItemSetting"):
        self.current_color = other.current_color

    def get_default_value(self):
        return self.default_color

    def set_default_value(self, value):
        self.default_color = value

    def restore_default_value(self):
        self.current_color = self.default_color

    def is_modified(self):
        return tuple(self.current_color) != tuple(self.default_color)

    @staticmethod
    def build_palette_rows():
        """Palette shown in the picker: tasteful lighter/base/darker variants of the
        StatPrism default colors, plus a neutrals row (white -> black) so backgrounds,
        frames, etc. can use white/gray/black. The "base" row is the set returned by
        Colors().get_color_list(), i.e. the defaults actually assigned to series."""
        base_colors = Colors().colors

        def _mix(c, target, t):
            return tuple(int(round(c[i] + (target[i] - c[i]) * t)) for i in range(3))

        white = (255, 255, 255)
        black = (0, 0, 0)
        lighter = [_mix(c, white, 0.45) for c in base_colors]
        darker = [_mix(c, black, 0.35) for c in base_colors]
        neutrals = [
            (255, 255, 255),
            (224, 224, 224),
            (176, 176, 176),
            (128, 128, 128),
            (96, 96, 96),
            (48, 48, 48),
            (0, 0, 0),
        ]
        return [lighter, list(base_colors), darker, neutrals]

    def setup(self):
        # Compact row: "label:" + a button showing the current color. Clicking the
        # button drops a palette popup next to it (no dimmed overlay); picking a tile
        # updates the swatch and closes the popup.
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QHBoxLayout,
            setup=lambda w, l: [l.setContentsMargins(5, 0, 5, 0), l.setSpacing(8)],
        )
        self.layout.addWidget(QLabel((self.label or "Color") + ":"))

        self.color_button = QPushButton()
        self.color_button.setFixedSize(70, 22)
        self.color_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_swatch()
        self.color_button.clicked.connect(self._open_popup)
        self.layout.addWidget(self.color_button)
        self.layout.addStretch()

    def _update_swatch(self):
        r, g, b = self.current_color
        set_stylesheet(
            self.color_button, css(background_color=f"rgb({r},{g},{b})", border=Style.General.border_elevated)
        )

    def _open_popup(self):
        popup = QFrame(self.color_button, Qt.WindowType.Popup)
        popup.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        set_stylesheet(
            popup, css(background_color=Style.Color.BackgroundElevated, border=Style.General.border_elevated)
        )
        grid = QGridLayout(popup)
        grid.setSpacing(4)
        grid.setContentsMargins(6, 6, 6, 6)

        for row, row_colors in enumerate(self.build_palette_rows()):
            for col, (pr, pg, pb) in enumerate(row_colors):
                btn = QPushButton(popup)
                btn.setFixedSize(22, 22)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                set_stylesheet(btn, css(background_color=f"rgb({pr},{pg},{pb})", border=Style.General.border_elevated))
                btn.clicked.connect(lambda _, c=(pr, pg, pb): self._select(c))
                grid.addWidget(btn, row, col)

        self._popup = popup
        popup.move(self.color_button.mapToGlobal(QPoint(0, self.color_button.height() + 2)))
        popup.show()

    def _select(self, color: Tuple[int, int, int]):
        self.current_color = color
        self._update_swatch()
        if self._popup is not None:
            self._popup.close()
            self._popup = None
        self.handler(Message(MessageType.EDITING_FINISHED, payload=None, caller_id=self.element_id))


class SingleLineTextResultItemSetting(_ValueDefaultsMixin, BasePanelElement):
    def __init__(self, label, current_value):
        super().__init__()

        self.label = label
        self.current_value = current_value
        self.default_value = current_value
        # ---
        self.line_edit = None

    def get_current_value(self):
        return self.current_value

    def set_up_from_other_instance(self, other: "SingleLineTextResultItemSetting"):
        self.current_value = other.current_value

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


class ContainerResultItemSetting(BasePanelElement):
    def __init__(self, items, add_stretch=False, label: str = None):
        super().__init__()
        self.items = items
        self.add_stretch = add_stretch
        self.label = label

    def set_up_from_other_instance(self, other: "ContainerResultItemSetting"):
        pass

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda widget, layout: [
                layout.setContentsMargins(2, 5, 2, 5),
                layout.setSpacing(10),
            ],
        )

        if self.label is not None:
            label = QLabel(text=self.label, parent=self.widget)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(label)

        for item in self.items:
            item.inject(self.widget, self.handler, self.element_id)
            item.setup()
            self.layout.addWidget(item.widget)
        if self.add_stretch:
            self.layout.addStretch()


class SliderResultItemSetting(_ValueDefaultsMixin, BasePanelElement):
    def __init__(self, label, current_value, min_value, max_value, step, add_stretch=False):
        super().__init__()
        self.label = label
        self.current_value = current_value
        self.default_value = current_value
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        assert add_stretch is False, "Stretch is not supported for SliderResultItemSetting"
        self.add_stretch = add_stretch
        # When False, the control is hidden from the settings panel (used to mark a setting that
        # doesn't apply to the current plot, e.g. legend size with no legend).
        self.enabled = True
        # ---
        self.slider = None
        self._debounce = None

    def get_current_value(self):
        return self.current_value

    def set_up_from_other_instance(self, other: "SliderResultItemSetting"):
        self.current_value = other.current_value

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
        # Click-to-position instead of the default page-step jump. The proxy style is kept on a
        # reference (self._slider_style) so it is not garbage-collected while the slider lives.
        self._slider_style = _AbsoluteSliderStyle(self.slider.style())
        self._slider_style.setParent(self.slider)
        self.slider.setStyle(self._slider_style)

        # Debounce: while dragging, the value updates live but the (expensive) re-render
        # is coalesced so it runs once after the drag settles, not on every tick.
        self._debounce = QTimer(self.widget)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(120)
        self._debounce.timeout.connect(self._emit_change)

        self.widget.setVisible(self.enabled)

    def slider_value_changed(self, value):
        self.current_value = self.min_value + value * self.step
        self._debounce.start()

    def _emit_change(self):
        self.handler(Message(MessageType.EDITING_FINISHED, payload=None, caller_id=self.element_id))


class CheckboxResultItemSetting(_ValueDefaultsMixin, BasePanelElement):
    def __init__(self, label, current_value, add_stretch=False):
        super().__init__()
        self.label = label
        self.current_value = current_value
        self.default_value = current_value
        assert add_stretch is False, "Stretch is not supported for CheckboxResultItemSetting"
        self.add_stretch = add_stretch
        self.enabled = True  # hidden from the settings panel when False
        # ---
        self.slider = None

    def get_current_value(self):
        return self.current_value

    def set_up_from_other_instance(self, other: "CheckboxResultItemSetting"):
        self.current_value = other.current_value

    def setup(self):
        self.large_checkbox = LargeCheckbox(label_text=self.label)
        self.large_checkbox.inject(self.parent_widget, self.handler, self.element_id)
        self.large_checkbox.setup()

        self.widget = self.large_checkbox.widget
        self.large_checkbox.widget.setChecked(self.current_value)
        self.large_checkbox.widget.stateChanged.connect(self.on_checkbox_state_changed)
        self.widget.setVisible(self.enabled)

    def on_checkbox_state_changed(self, state):
        self.current_value = state == Qt.CheckState.Checked.value
        self.handler(Message(MessageType.EDITING_FINISHED, payload=None, caller_id=self.element_id))


class DropdownResultItemSetting(_ValueDefaultsMixin, BasePanelElement):
    def __init__(self, label, current_value, items, add_stretch=False):
        super().__init__()
        self.label = label
        self.current_value = current_value
        self.default_value = current_value
        self.items = items
        assert add_stretch is False, "Stretch is not supported for DropdownResultItemSetting"
        self.add_stretch = add_stretch
        # ---
        self.combo_box = None

    def get_current_value(self):
        return self.current_value

    def set_up_from_other_instance(self, other: "DropdownResultItemSetting"):
        self.current_value = other.current_value

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda widget, layout: [
                layout.setContentsMargins(5, 0, 5, 0),
                layout.setSpacing(2),
            ],
        )
        self.label_widget = widget_in_layout(widget=QLabel(self.label), layout=self.layout)
        self.combo_box = widget_in_layout(
            widget=NoScrollComboBox(),
            layout=self.layout,
            setup=lambda widget, layout: [
                widget.addItems(self.items),
                widget.setCurrentText(self.current_value if self.current_value in self.items else self.items[0]),
                # connect last so the initial population does not emit a change
                widget.currentTextChanged.connect(self.on_changed),
            ],
        )

    def on_changed(self, value):
        self.current_value = value
        self.handler(Message(MessageType.EDITING_FINISHED, payload=None, caller_id=self.element_id))


# A standard QCheckBox whose label uses the regular font, unlike the larger, heavily-styled
# CheckboxResultItemSetting.
class PlainCheckboxResultItemSetting(_ValueDefaultsMixin, BasePanelElement):
    def __init__(self, label, current_value, add_stretch=False):
        super().__init__()
        self.label = label
        self.current_value = current_value
        self.default_value = current_value
        assert add_stretch is False, "Stretch is not supported for PlainCheckboxResultItemSetting"
        self.add_stretch = add_stretch
        self.enabled = True  # hidden from the settings panel when False
        # ---
        self.checkbox = None

    def get_current_value(self):
        return self.current_value

    def set_up_from_other_instance(self, other: "PlainCheckboxResultItemSetting"):
        self.current_value = other.current_value

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QHBoxLayout,
            setup=lambda w, l: [l.setContentsMargins(5, 0, 5, 0)],
        )
        self.checkbox = QCheckBox(self.label)
        self.checkbox.setChecked(bool(self.current_value))
        self.checkbox.stateChanged.connect(self.on_changed)
        self.layout.addWidget(self.checkbox)
        self.layout.addStretch()
        self.widget.setVisible(self.enabled)

    def on_changed(self, _state):
        self.current_value = self.checkbox.isChecked()
        self.handler(Message(MessageType.EDITING_FINISHED, payload=None, caller_id=self.element_id))
