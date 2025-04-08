#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider, QVBoxLayout

from src.common.elements.base.base import BasePanelElement
from src.common.elements.edit.edit import LabeledLineEdit
from src.common.elements.utility.layout_helpers import empty_widget, widget_in_layout
from src.common.messages import Message, MessageType
from src.common.size import SettingsPanelSize


class SingleLineTextResultItemSetting(BasePanelElement):
    def __init__(self, label, current_value):
        super().__init__()

        self.label = label
        self.current_value = current_value
        # ---
        self.line_edit = None

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
        )
        self.line_edit = LabeledLineEdit(label_text=self.label)
        self.line_edit.inject(self.widget, self.handler, self.element_id)
        self.line_edit.setup()
        self.line_edit.edit_widget.setText(self.current_value)
        self.layout.addWidget(self.line_edit.widget)
        self.line_edit.edit_widget.editingFinished.connect(self.on_edit_finished)

    def on_edit_finished(self):
        self.current_value = self.line_edit.edit_widget.text()
        self.handler(Message(MessageType.EDITING_FINISHED, payload=None, caller_id=self.element_id))


class NumberCaptionResultItemSetting(BasePanelElement):
    def __init__(self, current_number, current_caption):
        super().__init__()
        self.number = SingleLineTextResultItemSetting("Number:", current_number)
        self.caption = SingleLineTextResultItemSetting("Caption:", current_caption)

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
        self.layout.addStretch()

    def get_number(self):
        return self.number.current_value

    def get_caption(self):
        return self.caption.current_value


class SliderResultItemSetting(BasePanelElement):
    def __init__(self, label, current_value, min_value, max_value, step):
        super().__init__()
        self.label = label
        self.current_value = current_value
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        # ---
        self.slider = None

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda widget, layout: [(layout.setContentsMargins(0, 0, 0, 0), layout.setSpacing(0))],
        )
        self.layout_hbox = QHBoxLayout()

        self.layout_hbox.setContentsMargins(0, 5, 0, 5)
        self.layout_hbox.setSpacing(10)
        self.layout.addLayout(self.layout_hbox)

        self.label = widget_in_layout(
            widget=QLabel(self.label),
            layout=self.layout_hbox,
            setup=lambda widget, layout: [
                widget.setAlignment(Qt.AlignmentFlag.AlignRight),
            ],
        )

        self.slider = widget_in_layout(
            widget=QSlider(Qt.Orientation.Horizontal),
            layout=self.layout_hbox,
            setup=lambda widget, layout: [
                widget.setMinimum(0),
                widget.setMaximum(int((self.max_value - self.min_value) / self.step)),
                widget.valueChanged.connect(self.slider_value_changed),
                widget.setMaximumWidth(SettingsPanelSize.max_col_width),
            ],
        )
        self.layout.addStretch()

    def slider_value_changed(self, value):
        self.current_value = self.min_value + value * self.step
        self.handler(Message(MessageType.EDITING_FINISHED, payload=None, caller_id=self.element_id))
