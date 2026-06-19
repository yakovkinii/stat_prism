#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import ast

from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QListWidget,
)

from src.common.constant import ColumnType
from src.common.decorators import log_method_noarg
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.order import CustomListWidget
from src.pyside_ext.elements.utility.primitive_elements import NoScrollComboBox
from src.pyside_ext.markup import css
from src.pyside_ext.overlay_popup import OverlayPopup, show_color_picker
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig

_TYPES = [ColumnType.NOMINAL.value, ColumnType.ORDINAL.value, ColumnType.NUMERIC.value]
_MAX_SUMMARY_ITEMS = 8


def _to_python(value):
    return value.item() if hasattr(value, "item") else value


class IISPWACColumnEditor(ItemInSidePanelWithAutoConfig):
    """Per-column editor for the Preprocess module. Renders one card per column of
    the chosen data source, each allowing rename, target type, ordinal ordering and
    value mapping. Adapts to the data in configure() and only rebuilds the cards when
    the column set changes (so typing in a rename field does not lose focus)."""

    def __init__(self):
        super().__init__()
        self.handler_changed = None
        self.specs = {}  # original_name -> spec dict
        self.unique_values = {}  # original_name -> sorted list of (python) unique values
        self.original_types = {}  # original_name -> the column's original ColumnType value
        self.cards = []  # per-column widget bundles, in column order
        self.order = []  # current column order (original names)
        self._built_columns = None
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
        saved = kwargs.get(self.name) or []
        saved_by_original = {s["original"]: s for s in saved if isinstance(s, dict) and "original" in s}

        try:
            data = DATA_MANAGER.get_data_from_data_label(data_label=data_label, current_result_id=result_id)
            # The ID column is system-managed and must not be modifiable here; hide its card.
            columns = [col for col in data.get_all_columns_as_column_types() if col.column_type != ColumnType.ID]
        except Exception:
            columns = []

        self.order = [col.column_name for col in columns]
        self.original_types = {col.column_name: col.column_type.value for col in columns}
        self.unique_values = {}
        specs = {}
        for col in columns:
            uniques = self._sorted_unique(col)
            self.unique_values[col.column_name] = uniques
            specs[col.column_name] = self._spec_from(saved_by_original.get(col.column_name), col, uniques)
        self.specs = specs

        if self.order != self._built_columns:
            self._rebuild(columns)
            self._built_columns = list(self.order)
        else:
            self._refresh_all_summaries()

    def _sorted_unique(self, col):
        values = [_to_python(v) for v in col.data_series.dropna().unique()]
        if col.order:
            values.sort(key=lambda v: col.order.get(v, 0))
        else:
            try:
                values.sort()
            except TypeError:
                values.sort(key=lambda v: str(v))
        return values

    def _spec_from(self, saved, col, uniques):
        # The column may already carry a colour tag from upstream; keep it unless overridden.
        default_color = col.color if isinstance(col.color, str) and col.color else None
        if saved is None:
            return {
                "original": col.column_name,
                "new_name": "",
                "type": col.column_type.value,
                "order": None,
                "mapping": None,
                "remove": False,
                "color": default_color,
            }
        order = [v for v in (saved.get("order") or []) if v in uniques]
        if order:
            order = order + [v for v in uniques if v not in order]
        mapping = [[f, t] for f, t in (saved.get("mapping") or []) if f in uniques]
        return {
            "original": col.column_name,
            "new_name": saved.get("new_name") or "",
            "type": saved.get("type") if saved.get("type") in _TYPES else col.column_type.value,
            "order": order or None,
            "mapping": mapping or None,
            "remove": bool(saved.get("remove", False)),
            "color": saved.get("color", default_color),
        }

    def get_kwargs(self):
        return {self.name: [self.specs[name] for name in self.order if name in self.specs]}

    # ------------------------------------------------------------------ cards
    def _rebuild(self, columns):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.cards = []

        for index, col in enumerate(columns):
            name = col.column_name
            card = QFrame(self.widget)
            set_stylesheet(card, css(border=Style.General.border_elevated))
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(6, 6, 6, 6)
            card_layout.setSpacing(3)

            header = QHBoxLayout()
            title = QLabel(name, card)
            title.setToolTip(name)
            set_stylesheet(title, css(font_size=Style.FontSize.regular))
            header.addWidget(title)
            header.addStretch()

            # Compact, horizontally-aligned controls: colour tag, keep (checked = keep), copy↑, reset.
            color_btn = QPushButton(card)
            color_btn.setFixedSize(26, 24)
            color_btn.setToolTip("Column color tag (for grouping; e.g. by questionnaire)")
            color_btn.clicked.connect(lambda _=False, n=name: self._open_color_picker(n))
            header.addWidget(color_btn)

            keep_checkbox = QCheckBox(card)
            keep_checkbox.setToolTip("Keep this column (uncheck to remove it from the output)")
            keep_checkbox.setChecked(not self.specs[name].get("remove"))
            keep_checkbox.toggled.connect(lambda checked, n=name: self._on_keep(n, checked))
            header.addWidget(keep_checkbox)

            copy_btn = QPushButton("↑", card)
            copy_btn.setFixedSize(26, 24)
            if index > 0:
                copy_btn.setToolTip("Copy settings from the column above")
                copy_btn.clicked.connect(lambda _=False, n=name: self._copy_from_above(n))
            else:
                copy_btn.setEnabled(False)
                copy_btn.setToolTip("No column above to copy from")
            header.addWidget(copy_btn)

            reset_btn = QPushButton("⟲", card)
            reset_btn.setFixedSize(26, 24)
            reset_btn.setToolTip("Reset this column: original type, no order, no mapping")
            reset_btn.clicked.connect(lambda _=False, n=name: self._reset(n))
            header.addWidget(reset_btn)

            card_layout.addLayout(header)

            # Everything below the header is disabled when the column is set to be removed.
            body = QWidget(card)
            card_layout.addWidget(body)
            body_layout = QVBoxLayout(body)
            body_layout.setContentsMargins(0, 0, 0, 0)
            body_layout.setSpacing(3)

            rename = QLineEdit(body)
            rename.setPlaceholderText(name)
            rename.setText(self.specs[name]["new_name"])
            # Tooltip shows the full (new) name so it stays readable when the field is narrow.
            rename.setToolTip(self.specs[name]["new_name"] or name)
            rename.editingFinished.connect(lambda n=name, e=rename: self._on_rename(n, e))
            body_layout.addWidget(rename)

            map_row = QHBoxLayout()
            map_button = QPushButton("Map values…", body)
            map_button.clicked.connect(lambda _=False, n=name: self._open_mapping(n))
            map_summary = QLabel(body)
            map_summary.setWordWrap(True)
            set_stylesheet(map_summary, css(font_size=Style.FontSize.smaller, color=Style.Color.SecondaryText))
            map_row.addWidget(map_button)
            map_row.addWidget(map_summary, 1)
            body_layout.addLayout(map_row)

            type_row = QHBoxLayout()
            type_row.addWidget(QLabel("Type:", body))
            type_combo = NoScrollComboBox(body)
            type_combo.addItems(_TYPES)
            type_combo.setCurrentText(self.specs[name]["type"])
            type_combo.currentTextChanged.connect(lambda text, n=name: self._on_type(n, text))
            type_row.addWidget(type_combo)
            type_row.addStretch()
            body_layout.addLayout(type_row)

            order_row = QWidget(body)
            order_layout = QHBoxLayout(order_row)
            order_layout.setContentsMargins(0, 0, 0, 0)
            order_button = QPushButton("Order…", order_row)
            order_button.clicked.connect(lambda _=False, n=name: self._open_order(n))
            order_summary = QLabel(order_row)
            order_summary.setWordWrap(True)
            set_stylesheet(order_summary, css(font_size=Style.FontSize.smaller, color=Style.Color.SecondaryText))
            order_layout.addWidget(order_button)
            order_layout.addWidget(order_summary, 1)
            body_layout.addWidget(order_row)

            body.setEnabled(not self.specs[name].get("remove"))

            self.layout.addWidget(card)
            self.cards.append(
                {
                    "name": name,
                    "card": card,
                    "rename": rename,
                    "keep_checkbox": keep_checkbox,
                    "color_button": color_btn,
                    "type_combo": type_combo,
                    "order_row": order_row,
                    "order_summary": order_summary,
                    "map_summary": map_summary,
                    "body": body,
                }
            )

        self._refresh_all_summaries()

    def _card(self, name):
        for card in self.cards:
            if card["name"] == name:
                return card
        return None

    def _refresh_all_summaries(self):
        for card in self.cards:
            name = card["name"]
            spec = self.specs.get(name)
            if spec is None:
                continue
            is_ordinal = spec["type"] == ColumnType.ORDINAL.value
            card["order_row"].setVisible(is_ordinal)
            if is_ordinal:
                order_values = spec["order"] or self.unique_values.get(name, [])
                card["order_summary"].setText(self._format_order(order_values))
            card["map_summary"].setText(self._format_mapping(spec["mapping"]))
            self._apply_color_button(name)

    def _apply_color_button(self, name):
        card = self._card(name)
        if card is None or card.get("color_button") is None:
            return
        color = self.specs.get(name, {}).get("color")
        button = card["color_button"]
        if isinstance(color, str) and color:
            set_stylesheet(button, css(background=color, border="1px solid gray"))
        else:
            set_stylesheet(button, css(background="white", border="1px dashed gray"))

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

    def _on_rename(self, name, edit):
        self.specs[name]["new_name"] = edit.text().strip()
        edit.setToolTip(edit.text().strip() or name)
        self._changed()

    def _on_type(self, name, text):
        self.specs[name]["type"] = text
        self._refresh_all_summaries()
        self._changed()

    def _on_keep(self, name, checked):
        # Checked = keep the column; unchecked = remove it (and grey out its body).
        self.specs[name]["remove"] = not checked
        card = self._card(name)
        if card is not None and card.get("body") is not None:
            card["body"].setEnabled(checked)
        self._changed()

    def _reset(self, name):
        """Clear all user input for this column: original type, no order, no mapping, keep."""
        spec = self.specs[name]
        spec["new_name"] = ""
        spec["type"] = self.original_types.get(name, spec["type"])
        spec["order"] = None
        spec["mapping"] = None
        spec["remove"] = False
        spec["color"] = None

        card = self._card(name)
        if card is not None:
            self._suppress = True
            if card.get("rename") is not None:
                card["rename"].setText("")
            if card.get("keep_checkbox") is not None:
                card["keep_checkbox"].setChecked(True)
            card["type_combo"].setCurrentText(spec["type"])
            if card.get("body") is not None:
                card["body"].setEnabled(True)
            self._suppress = False
        self._refresh_all_summaries()
        self._changed()

    def _copy_from_above(self, name):
        index = self.order.index(name)
        if index == 0:
            return
        previous = self.specs[self.order[index - 1]]
        uniques = self.unique_values.get(name, [])
        spec = self.specs[name]

        spec["type"] = previous["type"]
        spec["color"] = previous.get("color")
        if previous["mapping"]:
            spec["mapping"] = [[f, t] for f, t in previous["mapping"] if f in uniques] or None
        if previous["order"]:
            kept = [v for v in previous["order"] if v in uniques]
            spec["order"] = (kept + [v for v in uniques if v not in kept]) or None

        card = self._card(name)
        if card is not None:
            self._suppress = True
            card["type_combo"].setCurrentText(spec["type"])
            self._suppress = False
        self._refresh_all_summaries()
        self._changed()

    # ------------------------------------------------------------------ popups
    def _open_color_picker(self, name):
        """Pick a pastel colour tag for the column (or None to clear)."""
        def choose(color):
            self.specs[name]["color"] = color
            self._apply_color_button(name)
            self._changed()

        show_color_picker(self.widget, choose)

    def _open_order(self, name):
        values = self.specs[name]["order"] or list(self.unique_values.get(name, []))

        content = QFrame()
        content.setMinimumWidth(600)
        set_stylesheet(content, css(background="white", border="1px solid gray"))
        layout = QHBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)

        list_widget = CustomListWidget(content)
        list_widget.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        list_widget.setMaximumHeight(800)
        set_stylesheet(
            list_widget,
            css(
                background=Style.Color.Background,
            ),
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
            self.specs[name]["order"] = ordered or None
            self._refresh_all_summaries()
            self._changed()

        OverlayPopup(self.widget, content, on_close=on_close)

    def _open_mapping(self, name):
        uniques = self.unique_values.get(name, [])
        existing = {f: t for f, t in (self.specs[name]["mapping"] or [])}

        content = QFrame()
        content.setFixedWidth(600)
        set_stylesheet(content, css(background="white", border="1px solid gray"))
        outer = QVBoxLayout(content)
        outer.setContentsMargins(12, 12, 12, 12)

        # Long value lists scroll vertically instead of overflowing the screen.
        scroll = QScrollArea(content)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(min(800, max(120, len(uniques) * 32)))
        set_stylesheet(scroll, css(border="none", background="white"))
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        rows = []
        for value in uniques:
            row = QHBoxLayout()
            left = QLabel(repr(value), inner)
            left.setMinimumWidth(200)
            # Tooltips keep the full source/target values readable when truncated.
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
                    target = text  # fall back to the raw string
                mapping.append([value, target])
            self.specs[name]["mapping"] = mapping or None
            self._refresh_all_summaries()
            self._changed()

        OverlayPopup(self.widget, content, on_close=on_close)

    # ------------------------------------------------------------------ misc
    def set_handler_changed(self, handler):
        self.handler_changed = handler

    def set_alert(self, column_names):
        """Outline the cards of the given (original) column names in red, e.g. when a
        column's cast to Numeric failed. Other cards are reset to the normal border."""
        names = set(column_names or [])
        for card in self.cards:
            border = "1px solid red" if card["name"] in names else Style.General.border_elevated
            set_stylesheet(card["card"], css(border=border))

    @log_method_noarg
    def clear_alert(self):
        for card in self.cards:
            set_stylesheet(card["card"], css(border=Style.General.border_elevated))
