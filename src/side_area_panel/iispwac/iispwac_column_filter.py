#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from src.common.constant import ColumnType
from src.common.decorators import log_method_noarg
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACColumnFilter(ItemInSidePanelWithAutoConfig):
    """Single-column filter that adapts to the column type:

    * numeric column -> an operation (==, !=, <, >, <=, >=) and a value;
    * ordinal / nominal column -> a checkbox per value (sorted by order for
      ordinal), where ticked values are kept.

    get_kwargs() returns a spec dict (or None) tagged with the column it was built
    for, so main() can safely no-op if the column selection has changed.
    """

    OPERATIONS = ["==", "!=", "<", ">", "<=", ">="]

    def __init__(self):
        super().__init__()
        self.handler_changed = None
        self.current_column = None
        self.current_mode = None
        self.value_pairs = []  # list of (original_value, QCheckBox) for categorical mode
        self.operation_combo = None
        self.value_edit = None

    def post_init(self, name, parent_widget):
        self.name = name

        self.widget = QWidget(parent_widget)
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        set_stylesheet(self.widget, css(border=Style.General.border_elevated))

        self.label = QLabel("Filter:", self.widget)
        self.layout.addWidget(self.label)

        self.container = QWidget(self.widget)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(3)
        self.layout.addWidget(self.container)

        self.clear_alert()

    def configure(self, **kwargs):
        spec = kwargs[self.name]
        data_label = kwargs.get("data_source") or "Auto"
        result_id = kwargs["result_id"]
        column_selector = kwargs.get("column_selector") or []
        selected = column_selector[0] if column_selector else []
        column_name = selected[0] if selected else None

        self.current_column = column_name
        self.current_mode = None
        self._clear_container()
        self.value_pairs = []
        self.operation_combo = None
        self.value_edit = None

        if column_name is None:
            return

        try:
            data = DATA_MANAGER.get_data_from_data_label(data_label=data_label, current_result_id=result_id)
            column = data[column_name]
        except Exception:
            return

        # Only restore the saved spec if it belongs to the currently-selected column.
        spec = spec if (spec is not None and spec.get("column") == column_name) else None

        if column.column_type == ColumnType.NUMERIC:
            self.current_mode = "numeric"
            self._build_numeric(spec)
        else:
            self.current_mode = "categorical"
            self._build_categorical(column, spec)

    def _clear_container(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _build_numeric(self, spec):
        row = QWidget(self.container)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(5)

        self.operation_combo = QComboBox(row)
        self.operation_combo.addItems(self.OPERATIONS)
        self.value_edit = QLineEdit(row)
        self.value_edit.setPlaceholderText("value")
        row_layout.addWidget(self.operation_combo)
        row_layout.addWidget(self.value_edit)
        self.container_layout.addWidget(row)

        operation = spec.get("operation") if spec else None
        value = (spec.get("value") if spec else "") or ""
        self.operation_combo.setCurrentText(operation if operation in self.OPERATIONS else "==")
        self.value_edit.setText(value)

        self.operation_combo.currentIndexChanged.connect(self.on_changed)
        # Recalculate only when the user finishes editing (Enter / focus-out), not on
        # every keystroke -- otherwise the panel rebuilds mid-typing and steals focus.
        self.value_edit.editingFinished.connect(self.on_changed)

    def _build_categorical(self, column, spec):
        values = list(column.data_series.dropna().unique())
        order = column.order or {}
        values.sort(key=lambda v: order.get(v, 0))

        kept = spec.get("kept_values") if spec else None
        kept_set = set(kept) if kept is not None else None

        for value in values:
            checkbox = QCheckBox(str(value), self.container)
            checkbox.setChecked(True if kept_set is None else (value in kept_set))
            checkbox.stateChanged.connect(self.on_changed)
            self.container_layout.addWidget(checkbox)
            self.value_pairs.append((value, checkbox))

    def get_kwargs(self):
        if self.current_mode == "numeric":
            return {
                self.name: {
                    "column": self.current_column,
                    "mode": "numeric",
                    "operation": self.operation_combo.currentText() if self.operation_combo else "==",
                    "value": self.value_edit.text() if self.value_edit else "",
                }
            }
        if self.current_mode == "categorical":
            return {
                self.name: {
                    "column": self.current_column,
                    "mode": "categorical",
                    "kept_values": [value for value, checkbox in self.value_pairs if checkbox.isChecked()],
                }
            }
        return {self.name: None}

    @log_method_noarg
    def set_alert(self):
        set_stylesheet(self.widget, css(border="1px solid red"))

    @log_method_noarg
    def clear_alert(self):
        set_stylesheet(self.widget, css(border=Style.General.border_elevated))

    def on_changed(self, *args):
        if self.handler_changed:
            self.handler_changed()
        self.on_recalculate()

    def set_handler_changed(self, handler):
        self.handler_changed = handler
