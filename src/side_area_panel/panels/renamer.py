#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QSizePolicy, QVBoxLayout, QWidget

from src.common.decorators import log_method
from src.common.messages import Message, MessageType
from src.common.ui_constructor import create_simple_tool_button_qta
from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.styling import Style

class Renamer(BasePanelElement):
    renamed = Signal(dict)  # Signal to emit renamed columns dict

    def __init__(self):
        super().__init__()
        self.line_edits = []
        self._original_names = []
        self._current_renamed = {}
        self._handler = None
        self.container_widget = None
        self.container_layout = None
        self.line_edits = []
        self._reset_buttons = []

    def inject(self, parent_widget, handler, element_id):
        super().inject(parent_widget, handler, element_id)
        self._handler = handler

    def setup(self):
        # Create the main widget and layout
        self.widget, self.layout = self._empty_widget_with_layout(QVBoxLayout)
        self.container_widget, self.container_layout = self._empty_widget_with_layout(QVBoxLayout, parent=self.widget)
        self.layout.addWidget(self.container_widget)

    @log_method
    def configure(self, original_names, current_renamed):
        self.line_edits = []
        self._reset_buttons = []

        self._original_names = original_names
        self._current_renamed = current_renamed
        # Clear previous widgets
        for i in reversed(range(self.container_layout.count())):
            widget = self.container_layout.itemAt(i).widget()
            if widget is not None:
                widget.hide()
                widget.deleteLater()

        # Add editable QLineEdit for each column (no labels)
        for idx, name in enumerate(self._original_names):
            row_widget = QWidget(self.container_widget)
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(2, 0, 2, 0)  # smaller left/right margins
            row_layout.setSpacing(2)  # smaller spacing between columns
            # QLineEdit for renaming
            edit = QLineEdit(self._current_renamed.get(name, name), parent=self.container_widget)
            edit.setMinimumWidth(200)
            edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            edit.setCursorPosition(0)  # Always show the beginning of the text
            edit.editingFinished.connect(self._make_edit_finished_handler(idx))
            self.line_edits.append(edit)
            row_layout.addWidget(edit)

            is_modified = name in self._current_renamed and self._current_renamed[name] != name
            reset_btn = create_simple_tool_button_qta(
                parent=self.container_widget,
                icon_path="fa.undo",
                icon_size=QSize(22, 22),
                color=Style.Color.Danger.value,
            )
            reset_btn.setToolTip("Restore original column name")
            reset_btn.setCursor(Qt.PointingHandCursor)
            reset_btn.clicked.connect(self._make_restore_handler(idx))
            reset_btn.setEnabled(is_modified)
            row_layout.addWidget(reset_btn)

            self._reset_buttons.append(reset_btn)
            row_layout.setStretch(0, 1)
            row_layout.setStretch(1, 0)
            row_widget.setLayout(row_layout)
            self.container_layout.addWidget(row_widget)

    def _make_edit_finished_handler(self, idx):
        def handler():
            self._on_edit_finished(idx)

        return handler

    def _make_restore_handler(self, idx):
        def handler():
            self._on_restore_clicked(idx)

        return handler

    def _on_edit_finished(self, idx):
        edit = self.line_edits[idx]
        old_name = self._original_names[idx]
        new_name = edit.text().strip()
        changed = False
        if new_name and new_name != old_name:
            self._current_renamed[old_name] = new_name
            changed = True
        elif new_name == old_name and old_name in self._current_renamed:
            del self._current_renamed[old_name]
            changed = True
        edit.setCursorPosition(0)
        edit.clearFocus()
        # Enable/disable reset button
        if hasattr(self, "_reset_buttons") and idx < len(self._reset_buttons):
            is_modified = old_name in self._current_renamed and self._current_renamed[old_name] != old_name
            self._reset_buttons[idx].setEnabled(is_modified)
        if changed and self._handler:
            msg = Message(
                message_type=MessageType.EDITING_FINISHED,
                payload={"renamed_columns": dict(self._current_renamed)},
                caller_id=self.element_id,
            )
            self._handler(msg)

    def _on_restore_clicked(self, idx):
        old_name = self._original_names[idx]
        edit = self.line_edits[idx]
        edit.setText(old_name)
        self._on_edit_finished(idx)
        edit.setCursorPosition(0)

    def _empty_widget_with_layout(self, layout_class, parent=None):
        widget = QWidget(parent or self.parent_widget)
        layout = layout_class(widget)
        return widget, layout
