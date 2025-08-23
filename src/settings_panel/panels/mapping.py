#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import logging
from typing import TYPE_CHECKING, Any, Dict

from PySide6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from src.common.decorators import log_method, log_method_noarg
from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.elements.title import Title
from src.settings_panel.panels.base import BasePanel

if TYPE_CHECKING:
    pass


class Mapping(BasePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Map Values to Numbers"),
            "mapping_visualizer": MappingVisualizer(),
        }
        self.setup(stretch=True, navigation_elements=True, ok_button=True)

    @log_method
    def configure(self, column_name, unique_values, current_mapping=None, caller_index=None, finished_handler=None):
        self.column_name = column_name
        self.unique_values = unique_values
        self.caller_index = caller_index
        self.finished_handler = finished_handler

        if caller_index is not None:
            self.back_button.setEnabled(True)
        else:
            logging.warning("Unexpected absence of caller_index")
            self.back_button.setEnabled(False)

        self.elements["mapping_visualizer"].configure(
            unique_values=unique_values, current_mapping=current_mapping or {}
        )

    @log_method_noarg
    def ok_button_pressed(self):
        mapping = self.elements["mapping_visualizer"].get_mapping()
        if self.finished_handler:
            self.finished_handler(self.column_name, mapping)
        self.activate_caller()


class MappingVisualizer(BasePanelElement):
    def __init__(self):
        super().__init__()
        self.spinboxes = []
        self.unique_values = []

    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.layout = QVBoxLayout(self.widget)

    def configure(self, unique_values, current_mapping):
        self.unique_values = unique_values
        self.spinboxes = []

        # Clear previous widgets
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.hide()
                widget.deleteLater()

        for value in unique_values:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(2, 0, 2, 0)
            row_layout.setSpacing(4)

            # Value label
            label = QLabel(str(value))
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            row_layout.addWidget(label)

            # Arrow
            arrow_label = QLabel("→")
            row_layout.addWidget(arrow_label)

            # Spinbox for mapping
            spinbox = QDoubleSpinBox()
            spinbox.setRange(-999999.0, 999999.0)
            spinbox.setDecimals(3)  # Changed from 2 to 3 for 0.001 precision
            spinbox.setSingleStep(0.001)  # Changed from 1.0 to 0.001
            spinbox.setFixedWidth(100)

            # Prevent text selection when spin buttons are pressed
            spinbox.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.UpDownArrows)
            spinbox.setKeyboardTracking(False)

            # Set default or current value
            if value in current_mapping:
                spinbox.setValue(current_mapping[value])
            else:
                # Try to parse as number, otherwise use index
                try:
                    spinbox.setValue(float(value))
                except (ValueError, TypeError):
                    spinbox.setValue(float(unique_values.index(value) + 1))

            self.spinboxes.append(spinbox)
            row_layout.addWidget(spinbox)

            row_layout.setStretch(0, 1)  # Label takes most space
            row_layout.setStretch(1, 0)  # Arrow fixed size
            row_layout.setStretch(2, 0)  # Spinbox fixed size

            self.layout.addWidget(row_widget)

    def get_mapping(self) -> Dict[Any, float]:
        mapping = {}
        for i, value in enumerate(self.unique_values):
            mapping[value] = self.spinboxes[i].value()
        return mapping
