#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import logging

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from src.common.messages import Message, MessageType
from src.common.ui_constructor import create_simple_tool_button_qta
from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class ColumnBlocksVisualizer(BasePanelElement):
    def __init__(self):
        super().__init__()
        self.columns = []
        self.column_widgets = {}
        self.mapping_settings = {}  # {column_name: {value: number_mapping}}
        self.invert_settings = {}  # {column_name: {"enabled": bool, "reference": float}}

    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.layout = QVBoxLayout(self.widget)

    def configure(self, columns, mapping_settings=None, invert_settings=None):
        """Configure the visualizer with columns and their settings"""
        logging.info(f"Configuring ColumnBlocksVisualizer with columns: {columns}")

        self.columns = columns
        self.mapping_settings = mapping_settings or {}
        self.invert_settings = invert_settings or {}

        # Clear previous widgets
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.hide()
                widget.deleteLater()

        self.column_widgets = {}

        # Add global settings section if there are columns
        if self.columns:
            self._create_global_settings()

        # Create widgets for each column
        for col_name in self.columns:
            col_widget = self._create_column_widget(col_name)
            self.column_widgets[col_name] = col_widget
            self.layout.addWidget(col_widget)

    def _create_global_settings(self):
        """Create global settings section for batch operations"""
        global_frame = QFrame()
        global_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        set_stylesheet(
            global_frame,
            css(
                "QFrame",
                border=Style.General.border_secondary_text,
                border_radius=Style.General.border_radius_small,
                padding=Style.General.padding_small,
                margin=Style.General.margin_tiny,
                background_color=Style.Color.BackgroundPanel,
            ),
        )

        layout = QVBoxLayout(global_frame)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # Title
        title_label = QLabel("<b>Global Settings</b>")
        layout.addWidget(title_label)

        # Global mapping button
        mapping_row = QWidget()
        mapping_layout = QHBoxLayout(mapping_row)
        mapping_layout.setContentsMargins(0, 0, 0, 0)
        mapping_layout.setSpacing(4)

        mapping_label = QLabel("Configure all value mappings:")
        mapping_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        mapping_layout.addWidget(mapping_label)

        global_mapping_btn = create_simple_tool_button_qta(
            parent=mapping_row, icon_path="mdi6.cog-sync-outline", icon_size=QSize(16, 16)
        )
        global_mapping_btn.setToolTip("Configure value mapping for all columns")
        global_mapping_btn.clicked.connect(self._global_mapping_handler)
        mapping_layout.addWidget(global_mapping_btn)

        layout.addWidget(mapping_row)

        # Global inversion button
        invert_row = QWidget()
        invert_layout = QHBoxLayout(invert_row)
        invert_layout.setContentsMargins(0, 0, 0, 0)
        invert_layout.setSpacing(4)

        invert_label = QLabel("Configure all inversion references:")
        invert_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        invert_layout.addWidget(invert_label)

        global_invert_btn = create_simple_tool_button_qta(
            parent=invert_row, icon_path="mdi6.cog-sync-outline", icon_size=QSize(16, 16)
        )
        global_invert_btn.setToolTip("Configure inversion reference for all columns")
        global_invert_btn.clicked.connect(self._global_inversion_handler)
        invert_layout.addWidget(global_invert_btn)

        layout.addWidget(invert_row)

        self.layout.addWidget(global_frame)

    def _create_column_widget(self, col_name):
        """Create a widget block for a single column"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        set_stylesheet(
            frame,
            css(
                "QFrame",
                border=Style.General.border_elevated,
                border_radius=Style.General.border_radius_small,
                padding=Style.General.padding_small,
                margin=Style.General.margin_tiny,
            ),
        )

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # Column name label
        name_label = QLabel(f"<b>{col_name}</b>")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        # Mapping summary for this column
        mapping_summary = QLabel()
        mapping_summary.setWordWrap(True)
        set_stylesheet(mapping_summary, css("QLabel", color=Style.Color.SecondaryText, font_size=Style.FontSize.small))
        mapping_summary.setVisible(False)
        layout.addWidget(mapping_summary)

        # Mapping row
        mapping_row = QWidget()
        mapping_layout = QHBoxLayout(mapping_row)
        mapping_layout.setContentsMargins(0, 0, 0, 0)
        mapping_layout.setSpacing(4)

        mapping_label = QLabel("Value mapping:")
        mapping_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        mapping_layout.addWidget(mapping_label)

        mapping_btn = create_simple_tool_button_qta(
            parent=mapping_row, icon_path="mdi6.cog-outline", icon_size=QSize(16, 16)
        )
        mapping_btn.setToolTip("Configure value mapping")
        mapping_btn.clicked.connect(self._make_mapping_handler(col_name))
        mapping_layout.addWidget(mapping_btn)

        layout.addWidget(mapping_row)

        # Inversion row
        invert_row = QWidget()
        invert_layout = QHBoxLayout(invert_row)
        invert_layout.setContentsMargins(0, 0, 0, 0)
        invert_layout.setSpacing(4)

        invert_checkbox = QCheckBox("Invert")
        is_inverted = self.invert_settings.get(col_name, {}).get("enabled", False)
        invert_checkbox.setChecked(is_inverted)
        invert_checkbox.stateChanged.connect(self._make_invert_checkbox_handler(col_name))
        invert_layout.addWidget(invert_checkbox)

        invert_config_btn = create_simple_tool_button_qta(
            parent=invert_row, icon_path="mdi6.cog-outline", icon_size=QSize(16, 16)
        )
        invert_config_btn.setToolTip("Configure inversion")
        invert_config_btn.setEnabled(is_inverted)
        invert_config_btn.clicked.connect(self._make_invert_config_handler(col_name))
        invert_layout.addWidget(invert_config_btn)

        # Reference value display
        ref_value = self.invert_settings.get(col_name, {}).get("reference", 0.0)
        ref_label = QLabel(f"(ref: {ref_value})")
        ref_label.setVisible(is_inverted)
        invert_layout.addWidget(ref_label)

        invert_layout.addStretch()
        layout.addWidget(invert_row)

        # Store references to update later
        frame.invert_checkbox = invert_checkbox
        frame.invert_config_btn = invert_config_btn
        frame.ref_label = ref_label
        frame.mapping_btn = mapping_btn
        frame.mapping_summary = mapping_summary

        # Update mapping summary for this column
        self._update_column_mapping_summary(frame, col_name)

        return frame

    def _make_mapping_handler(self, col_name):
        def handler():
            if self.handler:
                msg = Message(
                    message_type=MessageType.CLICKED,
                    payload={"action": "configure_mapping", "column": col_name},
                    caller_id=self.element_id,
                )
                self.handler(msg)

        return handler

    def _make_invert_checkbox_handler(self, col_name):
        def handler(state):
            is_checked = Qt.CheckState(state) == Qt.CheckState.Checked

            # Update settings
            if col_name not in self.invert_settings:
                self.invert_settings[col_name] = {}
            self.invert_settings[col_name]["enabled"] = is_checked

            # Update UI
            if col_name in self.column_widgets:
                widget = self.column_widgets[col_name]
                widget.invert_config_btn.setEnabled(is_checked)
                widget.ref_label.setVisible(is_checked)

            if self.handler:
                msg = Message(
                    message_type=MessageType.STATE_CHANGED,
                    payload={"action": "invert_toggled", "column": col_name, "enabled": is_checked},
                    caller_id=self.element_id,
                )
                self.handler(msg)

        return handler

    def _make_invert_config_handler(self, col_name):
        def handler():
            if self.handler:
                msg = Message(
                    message_type=MessageType.CLICKED,
                    payload={"action": "configure_inversion", "column": col_name},
                    caller_id=self.element_id,
                )
                self.handler(msg)

        return handler

    def _global_mapping_handler(self):
        """Handle global mapping configuration"""
        if self.handler:
            msg = Message(
                message_type=MessageType.CLICKED,
                payload={"action": "configure_global_mapping"},
                caller_id=self.element_id,
            )
            self.handler(msg)

    def _global_inversion_handler(self):
        """Handle global inversion configuration"""
        if self.handler:
            msg = Message(
                message_type=MessageType.CLICKED,
                payload={"action": "configure_global_inversion"},
                caller_id=self.element_id,
            )
            self.handler(msg)

    def update_mapping_settings(self, col_name, mapping):
        """Update mapping settings for a column"""
        self.mapping_settings[col_name] = mapping

        # Update the mapping summary for this column
        if col_name in self.column_widgets:
            self._update_column_mapping_summary(self.column_widgets[col_name], col_name)

        if self.handler:
            msg = Message(
                message_type=MessageType.STATE_CHANGED,
                payload={"action": "mapping_updated", "column": col_name, "mapping": mapping},
                caller_id=self.element_id,
            )
            self.handler(msg)

    def update_invert_reference(self, col_name, reference):
        """Update inversion reference for a column"""
        if col_name not in self.invert_settings:
            self.invert_settings[col_name] = {}
        self.invert_settings[col_name]["reference"] = reference

        # Update UI
        if col_name in self.column_widgets:
            widget = self.column_widgets[col_name]
            widget.ref_label.setText(f"(ref: {reference})")

        if self.handler:
            msg = Message(
                message_type=MessageType.STATE_CHANGED,
                payload={"action": "inversion_updated", "column": col_name, "reference": reference},
                caller_id=self.element_id,
            )
            self.handler(msg)

    def get_mapping_settings(self):
        return dict(self.mapping_settings)

    def get_invert_settings(self):
        return dict(self.invert_settings)

    def _update_column_mapping_summary(self, frame, col_name):
        """Update the mapping summary for a specific column"""
        mapping = self.mapping_settings.get(col_name, {})

        if not mapping:
            frame.mapping_summary.setVisible(False)
            return

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

        if is_identity:
            frame.mapping_summary.setVisible(False)
            return

        # Build summary text for non-identity mappings
        mapping_strs = []
        for original, mapped in sorted(mapping.items()):
            if str(original) != str(mapped):  # Only show non-identity mappings
                mapping_strs.append(f"'{original}' → {mapped}")

        if mapping_strs:
            summary_text = f"<i>Mappings: {', '.join(mapping_strs)}</i>"
            frame.mapping_summary.setText(summary_text)
            frame.mapping_summary.setVisible(True)
        else:
            frame.mapping_summary.setVisible(False)
