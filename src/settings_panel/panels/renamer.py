#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from PySide6.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QSizePolicy, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QSize
from src.pyside_ext.elements.base import BasePanelElement
from src.common.decorators import log_method
from src.modules.rename_columns.result import RenameColumnsStudyConfig
from src.modules.common.result.registry import RESULTS
from src.common.ui_constructor import create_simple_tool_button_qta

class Renamer(BasePanelElement):
    def __init__(self):
        super().__init__()
        self.line_edits = []

    def setup(self):
        # Create the main widget and layout
        self.widget, self.layout = self._empty_widget_with_layout(QVBoxLayout)
        self.container_widget, self.container_layout = self._empty_widget_with_layout(QVBoxLayout, parent=self.widget)
        self.layout.addWidget(self.container_widget)
        self.line_edits = []

    @log_method
    def configure(self, config: RenameColumnsStudyConfig, result_id: int):
        self.config = config
        self.result_id = result_id
        self.data = self.config.data
        self.line_edits = []
        self._original_names = self.data.column_names()
        # Clear previous widgets
        for i in reversed(range(self.container_layout.count())):
            widget = self.container_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        # Add editable QLineEdit for each column (no labels)
        for idx, name in enumerate(self._original_names):
            row_widget = QWidget(self.container_widget)
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 2, 0, 2)
            row_layout.setSpacing(6)
            # QLineEdit for renaming
            edit = QLineEdit(self.config.renamed_columns.get(name, name))
            edit.setMinimumWidth(200)
            edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            # Visual indicator for modified columns: thin black border
            if name in self.config.renamed_columns and self.config.renamed_columns[name] != name:
                edit.setStyleSheet("border: 1.2px solid #111; background: none;")
            else:
                edit.setStyleSheet("")
            edit.setCursorPosition(0)  # Always show the beginning of the text
            edit.editingFinished.connect(self._make_edit_finished_handler(idx))
            self.line_edits.append(edit)
            row_layout.addWidget(edit)
            # Qua icon reset button, slightly larger
            reset_btn = create_simple_tool_button_qta(
                parent=self.container_widget,
                icon_path="fa.undo",
                icon_size=QSize(22, 22),
            )
            reset_btn.setToolTip("Restore original column name")
            reset_btn.setCursor(Qt.PointingHandCursor)
            reset_btn.clicked.connect(self._make_restore_handler(idx))
            row_layout.addWidget(reset_btn)
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
        if new_name and new_name != old_name:
            self.config.renamed_columns[old_name] = new_name
            self.data.columns[idx].column_name = new_name
            self.data.update_lookups()
            self.config.data = self.data
            RESULTS[self.result_id].needs_update = True
            edit.setStyleSheet("border: 1.2px solid #111; background: none;")
            edit.setCursorPosition(0)
        elif new_name == old_name and old_name in self.config.renamed_columns:
            del self.config.renamed_columns[old_name]
            self.data.columns[idx].column_name = old_name
            self.data.update_lookups()
            self.config.data = self.data
            RESULTS[self.result_id].needs_update = True
            edit.setStyleSheet("")
            edit.setCursorPosition(0)
        # Remove focus to exit editing mode
        edit.clearFocus()

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
