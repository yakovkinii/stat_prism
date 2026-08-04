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


import logging

from PySide6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from src.common.constant import RARROW
from src.common.decorators import log_method, log_method_noarg
from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.elements.title import Title
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.panels.base import BasePanel


class InversionConfig(BasePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Configure Inversion"),
            "inversion_visualizer": InversionVisualizer(),
        }
        self.setup(stretch=True, navigation_elements=True, ok_button=True)

    @log_method
    def configure(
        self,
        column_name,
        min_value,
        max_value,
        current_reference=None,
        caller_index=None,
        finished_handler=None,
        unique_values=None,
    ):
        self.column_name = column_name
        self.caller_index = caller_index
        self.finished_handler = finished_handler

        if caller_index is not None:
            self.back_button.setEnabled(True)
        else:
            logging.warning("Unexpected absence of caller_index")
            self.back_button.setEnabled(False)

        default_reference = max_value + min_value if current_reference is None else current_reference

        self.elements["inversion_visualizer"].configure(
            min_value=min_value, max_value=max_value, current_reference=default_reference, unique_values=unique_values
        )

    @log_method_noarg
    def ok_button_pressed(self):
        reference = self.elements["inversion_visualizer"].get_reference()
        if self.finished_handler:
            self.finished_handler(self.column_name, reference)
        self.activate_caller()


class InversionVisualizer(BasePanelElement):
    def __init__(self):
        super().__init__()
        self.reference_spinbox = None

    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.layout = QVBoxLayout(self.widget)

    def configure(self, min_value, max_value, current_reference, unique_values=None):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.hide()
                widget.deleteLater()

        explanation = QLabel(f"Column range: {min_value} to {max_value}")
        explanation.setWordWrap(True)
        self.layout.addWidget(explanation)

        explanation2 = QLabel("Inversion formula: new_value = reference - old_value")
        explanation2.setWordWrap(True)
        self.layout.addWidget(explanation2)

        ref_widget = QWidget()
        ref_layout = QHBoxLayout(ref_widget)
        ref_layout.setContentsMargins(2, 0, 2, 0)

        ref_label = QLabel("Reference value:")
        ref_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        ref_layout.addWidget(ref_label)

        self.reference_spinbox = QDoubleSpinBox()
        self.reference_spinbox.setRange(-999999.0, 999999.0)
        self.reference_spinbox.setDecimals(3)
        self.reference_spinbox.setSingleStep(0.001)
        self.reference_spinbox.setValue(current_reference)
        self.reference_spinbox.setFixedWidth(Style.General.spinbox_width.value)

        # Prevent text selection when spin buttons are pressed
        self.reference_spinbox.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.UpDownArrows)
        self.reference_spinbox.setKeyboardTracking(False)
        ref_layout.addWidget(self.reference_spinbox)

        ref_layout.setStretch(0, 1)
        ref_layout.setStretch(1, 0)

        self.layout.addWidget(ref_widget)

        preview_label = QLabel("Preview:")
        self.layout.addWidget(preview_label)

        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)

        self.preview_labels = []

        if unique_values is not None and len(unique_values) > 0:
            sorted_values = sorted(unique_values)

            # Limit the preview to first 5 + last 5 so a long list does not clutter the panel.
            if len(sorted_values) > 10:
                display_values = sorted_values[:5] + ["..."] + sorted_values[-5:]
            else:
                display_values = sorted_values

            for value in display_values:
                if value == "...":
                    ellipsis_label = QLabel("... (more values) ...")
                    set_stylesheet(ellipsis_label, css("QLabel", font_style="italic"))
                    preview_layout.addWidget(ellipsis_label)
                    self.preview_labels.append(None)
                else:
                    preview_label = QLabel(f"{value} {RARROW} {current_reference - value}")
                    preview_layout.addWidget(preview_label)
                    self.preview_labels.append((preview_label, value))
        else:
            min_preview = QLabel(f"{min_value} {RARROW} {current_reference - min_value}")
            max_preview = QLabel(f"{max_value} {RARROW} {current_reference - max_value}")

            preview_layout.addWidget(min_preview)
            preview_layout.addWidget(max_preview)
            self.preview_labels = [(min_preview, min_value), (max_preview, max_value)]

        self.layout.addWidget(preview_widget)

        def update_preview():
            ref_val = self.reference_spinbox.value()
            for item in self.preview_labels:
                if item is not None:  # None marks an ellipsis row, which has no value
                    label, value = item
                    label.setText(f"{value} {RARROW} {ref_val - value}")

        self.reference_spinbox.valueChanged.connect(update_preview)

    def get_reference(self) -> float:
        return self.reference_spinbox.value()
