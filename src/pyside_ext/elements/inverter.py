#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging
from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.common.messages import Message, MessageType
from src.pyside_ext.elements.base import BasePanelElement


@dataclass
class InvertSettings:
    reference: float = 0.0


class Inverter(BasePanelElement):
    def __init__(self):
        super().__init__()
        self.checkboxes = []
        self.spinboxes = []
        self._columns = []
        self._invert_settings = {}
        self.container_widget = None
        self.container_layout = None

    def inject(self, parent_widget, handler, element_id):
        super().inject(parent_widget, handler, element_id)
        self._handler = handler

    def setup(self):
        self.widget, self.layout = self._empty_widget_with_layout(QVBoxLayout)
        self.container_widget, self.container_layout = self._empty_widget_with_layout(QVBoxLayout, parent=self.widget)
        self.layout.addWidget(self.container_widget)

    def configure(self, columns, invert_settings):
        logging.info(f"Configuring Inverter with columns: {columns} and invert_settings: {invert_settings}")
        self.checkboxes = []
        self.spinboxes = []
        self._columns = columns
        # Convert old format to new format if needed
        if invert_settings and isinstance(list(invert_settings.values())[0], bool):
            # Old format: {col: True/False}
            self._invert_settings = {col: InvertSettings() for col, inverted in invert_settings.items() if inverted}
        else:
            # New format: {col: InvertSettings}
            self._invert_settings = dict(invert_settings) if invert_settings else {}

        for i in reversed(range(self.container_layout.count())):
            widget = self.container_layout.itemAt(i).widget()
            if widget is not None:
                widget.hide()
                widget.deleteLater()

        for idx, col in enumerate(self._columns):
            row_widget = QWidget(self.container_widget)
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(2, 0, 2, 0)
            row_layout.setSpacing(4)

            # Column label
            label = QLabel(col, parent=self.container_widget)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            row_layout.addWidget(label)

            # Invert checkbox
            cb = QCheckBox("Invert", parent=self.container_widget)
            is_inverted = col in self._invert_settings
            cb.setChecked(is_inverted)
            cb.stateChanged.connect(self._make_checkbox_handler(idx))
            self.checkboxes.append(cb)
            row_layout.addWidget(cb)

            # Reference spinbox
            spinbox = QDoubleSpinBox(parent=self.container_widget)
            spinbox.setRange(-999999.0, 999999.0)
            spinbox.setDecimals(2)
            spinbox.setSingleStep(0.1)
            spinbox.setFixedWidth(80)
            if is_inverted and col in self._invert_settings:
                spinbox.setValue(self._invert_settings[col].reference)
            else:
                spinbox.setValue(0.0)
            spinbox.setEnabled(is_inverted)
            spinbox.valueChanged.connect(self._make_spinbox_handler(idx))
            self.spinboxes.append(spinbox)
            row_layout.addWidget(spinbox)

            row_layout.setStretch(0, 1)  # Label takes most space
            row_layout.setStretch(1, 0)  # Checkbox fixed size
            row_layout.setStretch(2, 0)  # Spinbox fixed size
            row_widget.setLayout(row_layout)
            self.container_layout.addWidget(row_widget)

    def _make_checkbox_handler(self, idx):
        def handler(state):
            col = self._columns[idx]
            spinbox = self.spinboxes[idx]

            if Qt.CheckState(state) == Qt.CheckState.Checked:
                self._invert_settings[col] = InvertSettings(reference=spinbox.value())
                spinbox.setEnabled(True)
            else:
                if col in self._invert_settings:
                    del self._invert_settings[col]
                spinbox.setEnabled(False)

            if self._handler:
                logging.info(f"checkbox handler; invert_settings={self._invert_settings}")
                msg = Message(
                    message_type=MessageType.STATE_CHANGED,
                    payload={"invert_settings": dict(self._invert_settings)},
                    caller_id=self.element_id,
                )
                self._handler(msg)

        return handler

    def _make_spinbox_handler(self, idx):
        def handler(value):
            col = self._columns[idx]
            if col in self._invert_settings:
                self._invert_settings[col].reference = value

                if self._handler:
                    logging.info(f"spinbox handler; invert_settings={self._invert_settings}")
                    msg = Message(
                        message_type=MessageType.STATE_CHANGED,
                        payload={"invert_settings": dict(self._invert_settings)},
                        caller_id=self.element_id,
                    )
                    self._handler(msg)

        return handler

    def _empty_widget_with_layout(self, layout_class, parent=None):
        widget = QWidget(parent or self.parent_widget)
        layout = layout_class(widget)
        return widget, layout
