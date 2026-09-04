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


import ast

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.common.constant import DARROW, MINUS, NDASH, RARROW, ColumnType
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.order import CustomListWidget
from src.pyside_ext.elements.utility.primitive_elements import NoScrollComboBox
from src.pyside_ext.markup import css
from src.pyside_ext.overlay_popup import OverlayPopup, show_color_picker
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig

_TYPES = [ColumnType.NOMINAL.value, ColumnType.ORDINAL.value, ColumnType.NUMERIC.value]
# Numeric normalizations offered for a Numeric target. "None" leaves the values as-is.
NORMALIZE_METHODS = ["None", "Z-score", "Stanine", "Center", "Min-max", "Log", "Rank"]


def _to_python(value):
    return value.item() if hasattr(value, "item") else value


class IISPWACTransformEditor(ItemInSidePanelWithAutoConfig):
    def __init__(self):
        super().__init__()
        self.handler_changed = None
        self.spec = None
        self.column_name = None
        self.columns = []
        self.column_type = None
        self.is_numeric_column = False
        self.unique_values = []
        self._built_column = None
        self._built_result_id = None
        self._suppress = False

    def post_init(self, name, parent_widget):
        self.name = name
        self.widget = QWidget(parent_widget)
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)

    def configure(self, **kwargs):
        data_label = kwargs.get("data_source") or "Auto"
        result_id = kwargs["result_id"]
        selector_value = kwargs.get("column_selector") or []
        selected = list(selector_value[0]) if selector_value else []
        saved = kwargs.get(self.name)

        columns = []
        if selected:
            try:
                data = DATA_MANAGER.get_data_from_data_label(data_label=data_label, current_result_id=result_id)
                names = data.column_names()
                columns = [data[c] for c in selected if c in names]
            except Exception:
                columns = []

        if not columns:
            self.spec = None
            self.columns = []
            self.column_name = None
            self.unique_values = []
            if self._built_column is not None or not getattr(self, "cards", None):
                self._rebuild_empty()
                self._built_column = None
            self._built_result_id = result_id
            return

        # Several columns can be transformed together; they share one spec applied over the
        # union of their values (each column only takes the entries it actually has).
        self.columns = [c.column_name for c in columns]
        self.column_name = self.columns[0]
        self.column_type = columns[0].column_type
        self.is_numeric_column = all(bool(c.is_numeric) for c in columns)
        self.unique_values = self._union_unique(columns)
        self.spec = self._spec_from(saved, columns)

        # Rebuild on a column change OR a different study (two Transform studies over the same
        # selection share column names, so the result-id check keeps their widgets independent).
        if self.columns != self._built_column or result_id != self._built_result_id:
            self._rebuild()
            self._built_column = list(self.columns)
            self._built_result_id = result_id
        else:
            self._refresh_visibility()

    def _union_unique(self, columns):
        """Ordered union of the unique values across the selected columns."""
        union = []
        for column in columns:
            for value in self._sorted_unique(column):
                if value not in union:
                    union.append(value)
        return union

    def _sorted_unique(self, column):
        values = [_to_python(v) for v in column.data_series.dropna().unique()]
        if column.order:
            values.sort(key=lambda v: column.order.get(v, 0))
        else:
            try:
                values.sort()
            except TypeError:
                values.sort(key=lambda v: str(v))
        return values

    def _spec_from(self, saved, columns):
        first = columns[0]
        names = [c.column_name for c in columns]
        default_color = first.color if isinstance(first.color, str) and first.color else None
        # Reuse a saved spec only when it covers exactly the same set of columns.
        if not isinstance(saved, dict) or set(saved.get("columns") or []) != set(names):
            return {
                "columns": names,
                "new_name": first.column_name,
                "mapping": None,
                "type": first.column_type.value,
                "order": None,
                "flip": False,
                "flip_reference": "",
                "normalize": "None",
                "color": default_color,
            }
        order = [v for v in (saved.get("order") or []) if v in self.unique_values]
        if order:
            order = order + [v for v in self.unique_values if v not in order]
        mapping = [[f, t] for f, t in (saved.get("mapping") or []) if f in self.unique_values]
        return {
            "columns": names,
            "new_name": saved.get("new_name") if saved.get("new_name") is not None else first.column_name,
            "mapping": mapping or None,
            "type": saved.get("type") if saved.get("type") in _TYPES else first.column_type.value,
            "order": order or None,
            "flip": bool(saved.get("flip", False)),
            "flip_reference": saved.get("flip_reference") or "",
            "normalize": saved.get("normalize") if saved.get("normalize") in NORMALIZE_METHODS else "None",
            "color": saved.get("color", default_color),
        }

    def get_kwargs(self):
        return {self.name: self.spec}

    def _clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.cards = []

    def _rebuild_empty(self):
        self._clear()
        hint = QLabel("Select a column above to configure its transform.", self.widget)
        set_stylesheet(hint, css(font_size=Style.FontSize.smaller, color=Style.Color.SecondaryText))
        self.layout.addWidget(hint)

    def _rebuild(self):
        self._clear()
        spec = self.spec

        card = QFrame(self.widget)
        set_stylesheet(card, css(border=Style.General.border_elevated))
        layout = QVBoxLayout(card)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # --- New name (default text = the current column name) ---
        # Renaming only applies to a single column; with several selected the field is hidden.
        multiple = len(self.columns) > 1
        self.rename_row = QWidget(card)
        rename_layout = QVBoxLayout(self.rename_row)
        rename_layout.setContentsMargins(0, 0, 0, 0)
        rename_layout.setSpacing(3)
        rename_layout.addWidget(QLabel("New name:", self.rename_row))
        self.rename_edit = QLineEdit(self.rename_row)
        self.rename_edit.setText(spec["new_name"])
        self.rename_edit.setToolTip(spec["new_name"] or self.column_name)
        self.rename_edit.editingFinished.connect(self._on_rename)
        rename_layout.addWidget(self.rename_edit)
        layout.addWidget(self.rename_row)
        self.rename_row.setVisible(not multiple)

        # --- Big actions: Map values + Type side by side; Order half-width below (ordinal) ---
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        self.map_button = QPushButton("Map values...", card)
        self.map_button.clicked.connect(self._open_mapping)
        grid.addWidget(self.map_button, 0, 0)

        self.type_combo = NoScrollComboBox(card)
        self.type_combo.addItems(_TYPES)
        self.type_combo.setCurrentText(spec["type"])
        self.type_combo.currentTextChanged.connect(self._on_type)
        grid.addWidget(self.type_combo, 0, 1)

        self.order_button = QPushButton("Order...", card)
        self.order_button.clicked.connect(self._open_order)
        grid.addWidget(self.order_button, 1, 0)  # half-width, aligned under Map values
        layout.addLayout(grid)

        # --- Flip (ordinal only) ---
        self.flip_row = QWidget(card)
        flip_layout = QHBoxLayout(self.flip_row)
        flip_layout.setContentsMargins(0, 0, 0, 0)
        self.flip_check = QCheckBox("Flip", self.flip_row)
        self.flip_check.setChecked(spec["flip"])
        self.flip_check.toggled.connect(self._on_flip)
        flip_layout.addWidget(self.flip_check)
        flip_layout.addWidget(QLabel("ref:", self.flip_row))
        self.flip_ref_edit = QLineEdit(self.flip_row)
        self.flip_ref_edit.setPlaceholderText("auto")
        self.flip_ref_edit.setText(spec["flip_reference"])
        self.flip_ref_edit.editingFinished.connect(self._on_flip_ref)
        flip_layout.addWidget(self.flip_ref_edit, 1)
        flip_info = QPushButton("?", self.flip_row)
        flip_info.setFixedSize(24, 24)
        flip_info.clicked.connect(self._open_flip_explanation)
        flip_layout.addWidget(flip_info)
        layout.addWidget(self.flip_row)

        # --- Normalize (numeric only) ---
        self.normalize_row = QWidget(card)
        norm_layout = QHBoxLayout(self.normalize_row)
        norm_layout.setContentsMargins(0, 0, 0, 0)
        norm_layout.addWidget(QLabel("Normalize:", self.normalize_row))
        self.normalize_combo = NoScrollComboBox(self.normalize_row)
        self.normalize_combo.addItems(NORMALIZE_METHODS)
        self.normalize_combo.setCurrentText(spec["normalize"])
        self.normalize_combo.currentTextChanged.connect(self._on_normalize)
        norm_layout.addWidget(self.normalize_combo)
        norm_layout.addStretch()
        layout.addWidget(self.normalize_row)

        # --- Color ---
        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Color:", card))
        self.color_button = QPushButton(card)
        self.color_button.setFixedSize(26, 24)
        self.color_button.clicked.connect(self._open_color_picker)
        color_row.addWidget(self.color_button)
        color_row.addStretch()
        layout.addLayout(color_row)

        self.cards = [card]
        self.layout.addWidget(card)
        self._refresh_visibility()

    def _refresh_visibility(self):
        if self.spec is None:
            return
        is_ordinal = self.spec["type"] == ColumnType.ORDINAL.value
        is_numeric = self.spec["type"] == ColumnType.NUMERIC.value
        self.order_button.setVisible(is_ordinal)
        self.flip_row.setVisible(is_ordinal)
        self.normalize_row.setVisible(is_numeric)
        # Bold the action buttons when they carry a setting (replaces the old text summaries).
        self._style_action_button(self.map_button, self._has_mapping(self.spec))
        self._style_action_button(self.order_button, is_ordinal and self.spec.get("order") is not None)
        self._apply_color_button()

    @staticmethod
    def _has_mapping(spec) -> bool:
        return any(f != t for f, t in (spec.get("mapping") or []))

    @staticmethod
    def _style_action_button(button, applied: bool):
        font = button.font()
        font.setBold(applied)
        button.setFont(font)

    def _apply_color_button(self):
        color = self.spec.get("color")
        if isinstance(color, str) and color:
            set_stylesheet(self.color_button, css(background=color, border="1px solid gray"))
        else:
            set_stylesheet(
                self.color_button,
                css(background=Style.Color.BackgroundEdit, border=f"1px dashed {Style.Color.BorderElevated}"),
            )

    def _changed(self):
        if self._suppress:
            return
        if self.handler_changed:
            self.handler_changed()
        self.on_recalculate()

    def _on_rename(self):
        self.spec["new_name"] = self.rename_edit.text().strip()
        self.rename_edit.setToolTip(self.spec["new_name"] or self.column_name)
        self._changed()

    def _on_type(self, text):
        self.spec["type"] = text
        self._refresh_visibility()
        self._changed()

    def _on_flip(self, checked):
        self.spec["flip"] = bool(checked)
        self._changed()

    def _on_flip_ref(self):
        self.spec["flip_reference"] = self.flip_ref_edit.text().strip()
        self._changed()

    def _on_normalize(self, text):
        self.spec["normalize"] = text
        self._changed()

    def _open_color_picker(self):
        def choose(color):
            self.spec["color"] = color
            self._apply_color_button()
            self._changed()

        show_color_picker(self.widget, choose)

    def _open_order(self):
        natural = list(self.unique_values)
        values = self.spec["order"] or natural

        content = QFrame()
        content.setMinimumWidth(600)
        set_stylesheet(
            content, css(background=Style.Color.BackgroundElevated, border=f"1px solid {Style.Color.BorderElevated}")
        )
        outer = QVBoxLayout(content)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(8)
        top = QHBoxLayout()

        list_widget = CustomListWidget(content)
        list_widget.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        list_widget.setMaximumHeight(800)
        set_stylesheet(
            list_widget,
            css(background=Style.Color.Background),
            css(selector="QListWidget::item", background=Style.Color.BackgroundPanel, margin="2px"),
        )

        def populate(order_values):
            list_widget.clear()
            for value in order_values:
                list_widget.add_custom_item(value, str(value))

        populate(values)
        top.addWidget(list_widget)

        hint = QLabel(f"SMALL\n{DARROW * 6}\nLARGE", content)
        set_stylesheet(hint, css(font_size=Style.FontSize.regular, color=Style.Color.SecondaryText))
        top.addWidget(hint)
        outer.addLayout(top)

        reset_button = QPushButton("Reset order", content)
        reset_button.setToolTip("Restore the natural (data) order")
        reset_button.clicked.connect(lambda: populate(natural))
        outer.addWidget(reset_button, alignment=Qt.AlignmentFlag.AlignLeft)

        def on_close():
            ordered = []
            for i in range(list_widget.count()):
                item_widget = list_widget.itemWidget(list_widget.item(i))
                if item_widget is not None:
                    ordered.append(item_widget.value)
            self.spec["order"] = ordered if (ordered and ordered != natural) else None
            self._refresh_visibility()
            self._changed()

        OverlayPopup(self.widget, content, on_close=on_close)

    def _open_mapping(self):
        uniques = self.unique_values
        existing = {f: t for f, t in (self.spec["mapping"] or [])}

        content = QFrame()
        content.setFixedWidth(600)
        set_stylesheet(
            content, css(background=Style.Color.BackgroundElevated, border=f"1px solid {Style.Color.BorderElevated}")
        )
        outer = QVBoxLayout(content)
        outer.setContentsMargins(12, 12, 12, 12)

        scroll = QScrollArea(content)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(min(800, max(120, len(uniques) * 32)))
        set_stylesheet(scroll, css(border="none", background=Style.Color.BackgroundElevated))
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        rows = []
        for value in uniques:
            row = QHBoxLayout()
            left = QLabel(repr(value), inner)
            left.setMinimumWidth(200)
            left.setToolTip(repr(value))
            set_stylesheet(left, css(font_size=Style.FontSize.smaller))
            row.addWidget(left)
            arrow = QLabel(RARROW, inner)
            set_stylesheet(arrow, css(font_size=Style.FontSize.smaller))
            row.addWidget(arrow)
            edit = QLineEdit(inner)
            edit.setText(repr(existing[value] if value in existing else value))
            edit.setToolTip(edit.text())
            edit.textChanged.connect(edit.setToolTip)
            set_stylesheet(edit, css(font_size=Style.FontSize.smaller))
            row.addWidget(edit, 1)
            layout.addLayout(row)
            rows.append((value, edit))

        scroll.setWidget(inner)
        outer.addWidget(scroll)

        reset_button = QPushButton("Reset mapping", content)
        reset_button.setToolTip("Clear the mapping (map every value to itself)")
        reset_button.clicked.connect(lambda: [edit.setText(repr(value)) for value, edit in rows])
        outer.addWidget(reset_button, alignment=Qt.AlignmentFlag.AlignLeft)

        def on_close():
            mapping = []
            for value, edit in rows:
                text = edit.text().strip()
                try:
                    target = ast.literal_eval(text)
                except (ValueError, SyntaxError):
                    target = text
                mapping.append([value, target])
            if all(f == t for f, t in mapping):
                mapping = None
            self.spec["mapping"] = mapping
            self._refresh_visibility()
            self._changed()

        OverlayPopup(self.widget, content, on_close=on_close)

    def _open_flip_explanation(self):
        """Explain the flip and preview each value -> (reference - value)."""
        numeric = pd.to_numeric(pd.Series(self.unique_values), errors="coerce").dropna()
        ref_text = (self.spec.get("flip_reference") or "").strip()
        try:
            reference = float(ref_text) if ref_text else (numeric.max() + numeric.min() if not numeric.empty else 0.0)
        except ValueError:
            reference = numeric.max() + numeric.min() if not numeric.empty else 0.0

        content = QFrame()
        content.setMinimumWidth(420)
        set_stylesheet(
            content, css(background=Style.Color.BackgroundElevated, border=f"1px solid {Style.Color.BorderElevated}")
        )
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        explanation = QLabel(
            f"Flip reverses the scale: every value x becomes (reference {MINUS} x), so the highest "
            "value swaps with the lowest. The reference defaults to (max + min) of the observed "
            "values; set it manually when some possible values do not appear in the data "
            f"(e.g. a 1{NDASH}5 Likert where nobody picked 5 {RARROW} set reference to 6).",
            content,
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        ref_label = QLabel(f"Reference = {reference:g}", content)
        set_stylesheet(ref_label, css(font_size=Style.FontSize.regular))
        layout.addWidget(ref_label)

        for value in sorted(numeric.unique()):
            layout.addWidget(QLabel(f"{value:g}  {RARROW}  {reference - value:g}", content))

        OverlayPopup(self.widget, content)

    def set_handler_changed(self, handler):
        self.handler_changed = handler

    def set_alert(self):
        pass

    def clear_alert(self):
        for card in getattr(self, "cards", []):
            set_stylesheet(card, css(border=Style.General.border_elevated))
