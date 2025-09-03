#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class MappingSummary(BasePanelElement):
    def __init__(self):
        super().__init__()
        self.mappings_label = None

    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.layout = QVBoxLayout(self.widget)

        self.mappings_label = QLabel()
        self.mappings_label.setWordWrap(True)
        set_stylesheet(
            self.mappings_label,
            css(
                color=Style.Color.SecondaryText,
                font_size=Style.FontSize.small
            )
        )
        self.layout.addWidget(self.mappings_label)

        # Initially hidden
        self.widget.setVisible(False)

    def update_mappings(self, mapping_settings):
        """Update the displayed mapping summary"""
        if not mapping_settings:
            self.widget.setVisible(False)
            return

        # Filter out empty mappings and identity mappings
        active_mappings = {}
        for col_name, mapping in mapping_settings.items():
            if mapping:  # Not empty
                # Check if this is an identity mapping (values map to themselves)
                is_identity = all(
                    str(key) == str(value)
                    or (
                        isinstance(value, (int, float))
                        and isinstance(key, str)
                        and str(key) == str(int(value))
                        and float(key) == value
                    )
                    for key, value in mapping.items()
                )
                if not is_identity:
                    active_mappings[col_name] = mapping

        if not active_mappings:
            self.widget.setVisible(False)
            return

        # Build summary text
        summary_lines = ["<b>Value Mappings:</b>"]
        for col_name, mapping in active_mappings.items():
            mapping_strs = []
            for original, mapped in sorted(mapping.items()):
                if str(original) != str(mapped):  # Only show non-identity mappings
                    mapping_strs.append(f"'{original}' → {mapped}")

            if mapping_strs:
                summary_lines.append(f"<b>{col_name}:</b> {', '.join(mapping_strs)}")

        if len(summary_lines) > 1:  # More than just the header
            self.mappings_label.setText("<br>".join(summary_lines))
            self.widget.setVisible(True)
        else:
            self.widget.setVisible(False)
