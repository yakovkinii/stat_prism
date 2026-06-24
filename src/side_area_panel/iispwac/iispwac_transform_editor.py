#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import ast

from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.common.constant import ColumnType
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.order import CustomListWidget
from src.pyside_ext.elements.utility.primitive_elements import NoScrollComboBox
from src.pyside_ext.markup import css
from src.pyside_ext.overlay_popup import OverlayPopup, show_color_picker
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig

_TYPES = [ColumnType.NOMINAL.value, ColumnType.ORDINAL.value, ColumnType.NUMERIC.value]
# Numeric normalisations offered for a Numeric target. "None" leaves the values as-is.
NORMALIZE_METHODS = ["None", "Z-score", "Stanine", "Center", "Min-max", "Log", "Rank"]
_MAX_SUMMARY_ITEMS = 8


def _to_python(value):
    return value.item() if hasattr(value, "item") else value


class IISPWACTransformEditor(ItemInSidePanelWithAutoConfig):
    """Single-column transform editor (a one-column sibling of the Preprocess editor).
    Reads the column chosen in the sibling column selector and configures, in order:
    new name, value mapping (popup), target type, ordinal ordering (popup), an optional
    ordinal flip (reference + explanation popup), a numeric normalisation, and a colour
    tag. The selected column is replaced in place; nothing is duplicated."""

    def __init__(self):
        super().__init__()
        self.handler_changed = None
        self.spec = None
        self.column_name = None
        self.column_type = None
        self.is_numeric_column = False
        self.unique_values = []
        self._built_column = None
        self._suppress = False

    # ------------------------------------------------------------------ layout
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
        column_name = selected[0] if selected else None
        saved = kwargs.get(self.name)

        column = None
        if column_name is not None:
            try:
                data = DATA_MANAGER.get_data_from_data_label(data_label=data_label, current_result_id=result_id)
                if column_name in data.column_names():
                    column = data[column_name]
            except Exception:
                column = None

        if column is None:
            self.spec = None
            self.column_name = None
            self.unique_values = []
            if self._built_column is not None or not getattr(self, "cards", None):
                self._rebuild_empty()
                self._built_column = None
            return

        self.column_name = column_name
        self.column_type = column.column_type
        self.is_numeric_column = bool(column.is_numeric)
        self.unique_values = self._sorted_unique(column)
        self.spec = self._spec_from(saved, column)

        if column_name != self._built_column:
            self._rebuild()
            self._built_column = column_name
        else:
            self._refresh_visibility()

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

    def _spec_from(self, saved, column):
        default_color = column.color if isinstance(column.color, str) and column.color else None
        # Reuse a saved spec only when it belongs to this same column.
        if not isinstance(saved, dict) or saved.get("column") != column.column_name:
            return {
                "column": column.column_name,
                "new_name": column.column_name,
                "mapping": None,
                "type": column.column_type.value,
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
            "column": column.column_name,
            "new_name": saved.get("new_name") if saved.get("new_name") is not None else column.column_name,
            "mapping": mapping or None,
            "type": saved.get("type") if saved.get("type") in _TYPES else column.column_type.value,
            "order": order or None,
            "flip": bool(saved.get("flip", False)),
            "flip_reference": saved.get("flip_reference") or "",
            "normalize": saved.get("normalize") if saved.get("normalize") in NORMALIZE_METHODS else "None",
            "color": saved.get("color", default_color),
        }

    def get_kwargs(self):
        return {self.name: self.spec}

    # ------------------------------------------------------------------ build
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
        layout.addWidget(QLabel("New name:", card))
        self.rename_edit = QLineEdit(card)
        self.rename_edit.setText(spec["new_name"])
        self.rename_edit.setToolTip(spec["new_name"] or self.column_name)
        self.rename_edit.editingFinished.connect(self._on_rename)
        layout.addWidget(self.rename_edit)

        # --- Map values ---
        map_row = QHBoxLayout()
        map_button = QPushButton("Map values…", card)
        map_button.clicked.connect(self._open_mapping)
        self.map_summary = QLabel(card)
        self.map_summary.setWordWrap(True)
        set_stylesheet(self.map_summary, css(font_size=Style.FontSize.smaller, color=Style.Color.SecondaryText))
        map_row.addWidget(map_button)
        map_row.addWidget(self.map_summary, 1)
        layout.addLayout(map_row)

        # --- Type ---
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:", card))
        self.type_combo = NoScrollComboBox(card)
        self.type_combo.addItems(_TYPES)
        self.type_combo.setCurrentText(spec["type"])
        self.type_combo.currentTextChanged.connect(self._on_type)
        type_row.addWidget(self.type_combo)
        type_row.addStretch()
        layout.addLayout(type_row)

        # --- Order (ordinal only) ---
        self.order_row = QWidget(card)
        order_layout = QHBoxLayout(self.order_row)
        order_layout.setContentsMargins(0, 0, 0, 0)
        order_button = QPushButton("Order…", self.order_row)
        order_button.clicked.connect(self._open_order)
        self.order_summary = QLabel(self.order_row)
        self.order_summary.setWordWrap(True)
        set_stylesheet(self.order_summary, css(font_size=Style.FontSize.smaller, color=Style.Color.SecondaryText))
        order_layout.addWidget(order_button)
        order_layout.addWidget(self.order_summary, 1)
        layout.addWidget(self.order_row)

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

        # --- Colour ---
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

    # ------------------------------------------------------------------ refresh
    def _refresh_visibility(self):
        if self.spec is None:
            return
        is_ordinal = self.spec["type"] == ColumnType.ORDINAL.value
        is_numeric = self.spec["type"] == ColumnType.NUMERIC.value
        self.order_row.setVisible(is_ordinal)
        self.flip_row.setVisible(is_ordinal)
        self.normalize_row.setVisible(is_numeric)
        if is_ordinal:
            order_values = self.spec["order"] or self.unique_values
            self.order_summary.setText(self._format_order(order_values))
        self.map_summary.setText(self._format_mapping(self.spec["mapping"]))
        self._apply_color_button()

    def _apply_color_button(self):
        color = self.spec.get("color")
        if isinstance(color, str) and color:
            set_stylesheet(self.color_button, css(background=color, border="1px solid gray"))
        else:
            set_stylesheet(self.color_button, css(background=Style.Color.BackgroundEdit, border=f"1px dashed {Style.Color.BorderElevated}"))

    @staticmethod
    def _format_order(values):
        shown = [str(v) for v in values[:_MAX_SUMMARY_ITEMS]]
        if len(values) > _MAX_SUMMARY_ITEMS:
            shown.append("…")
        return " < ".join(shown)

    @staticmethod
    def _format_mapping(mapping):
        if not mapping:
            return ""
        parts = [f"{f!r} → {t!r}" for f, t in mapping if f != t]
        if not parts:
            return ""
        text = ", ".join(parts[:_MAX_SUMMARY_ITEMS])
        if len(parts) > _MAX_SUMMARY_ITEMS:
            text += ", …"
        return text

    # ------------------------------------------------------------------ events
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

    # ------------------------------------------------------------------ popups
    def _open_color_picker(self):
        def choose(color):
            self.spec["color"] = color
            self._apply_color_button()
            self._changed()

        show_color_picker(self.widget, choose)

    def _open_order(self):
        values = self.spec["order"] or list(self.unique_values)

        content = QFrame()
        content.setMinimumWidth(600)
        set_stylesheet(content, css(background=Style.Color.BackgroundElevated, border=f"1px solid {Style.Color.BorderElevated}"))
        layout = QHBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)

        list_widget = CustomListWidget(content)
        list_widget.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        list_widget.setMaximumHeight(800)
        set_stylesheet(
            list_widget,
            css(background=Style.Color.Background),
            css(selector="QListWidget::item", background=Style.Color.BackgroundPanel, margin="2px"),
        )
        for value in values:
            list_widget.add_custom_item(value, str(value))
        layout.addWidget(list_widget)

        hint = QLabel("SMALL\n↓↓↓↓↓↓\nLARGE", content)
        set_stylesheet(hint, css(font_size=Style.FontSize.regular, color=Style.Color.SecondaryText))
        layout.addWidget(hint)

        def on_close():
            ordered = []
            for i in range(list_widget.count()):
                item_widget = list_widget.itemWidget(list_widget.item(i))
                if item_widget is not None:
                    ordered.append(item_widget.value)
            self.spec["order"] = ordered or None
            self._refresh_visibility()
            self._changed()

        OverlayPopup(self.widget, content, on_close=on_close)

    def _open_mapping(self):
        uniques = self.unique_values
        existing = {f: t for f, t in (self.spec["mapping"] or [])}

        content = QFrame()
        content.setFixedWidth(600)
        set_stylesheet(content, css(background=Style.Color.BackgroundElevated, border=f"1px solid {Style.Color.BorderElevated}"))
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
            arrow = QLabel("→", inner)
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

        def on_close():
            mapping = []
            for value, edit in rows:
                text = edit.text().strip()
                try:
                    target = ast.literal_eval(text)
                except (ValueError, SyntaxError):
                    target = text
                mapping.append([value, target])
            self.spec["mapping"] = mapping or None
            self._refresh_visibility()
            self._changed()

        OverlayPopup(self.widget, content, on_close=on_close)

    def _open_flip_explanation(self):
        """Explain the flip and preview each value -> (reference - value)."""
        import pandas as pd

        numeric = pd.to_numeric(pd.Series(self.unique_values), errors="coerce").dropna()
        ref_text = (self.spec.get("flip_reference") or "").strip()
        try:
            reference = float(ref_text) if ref_text else (numeric.max() + numeric.min() if not numeric.empty else 0.0)
        except ValueError:
            reference = numeric.max() + numeric.min() if not numeric.empty else 0.0

        content = QFrame()
        content.setMinimumWidth(420)
        set_stylesheet(content, css(background=Style.Color.BackgroundElevated, border=f"1px solid {Style.Color.BorderElevated}"))
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        explanation = QLabel(
            "Flip reverses the scale: every value x becomes (reference − x), so the highest "
            "value swaps with the lowest. The reference defaults to (max + min) of the observed "
            "values; set it manually when some possible values do not appear in the data "
            "(e.g. a 1–5 Likert where nobody picked 5 → set reference to 6).",
            content,
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        ref_label = QLabel(f"Reference = {reference:g}", content)
        set_stylesheet(ref_label, css(font_size=Style.FontSize.regular))
        layout.addWidget(ref_label)

        for value in sorted(numeric.unique()):
            layout.addWidget(QLabel(f"{value:g}  →  {reference - value:g}", content))

        OverlayPopup(self.widget, content)

    # ------------------------------------------------------------------ misc
    def set_handler_changed(self, handler):
        self.handler_changed = handler

    def set_alert(self):
        pass

    def clear_alert(self):
        for card in getattr(self, "cards", []):
            set_stylesheet(card, css(border=Style.General.border_elevated))
