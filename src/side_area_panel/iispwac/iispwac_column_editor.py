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

from PySide6.QtCore import QEvent, Qt
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

from src.common.constant import DARROW, RARROW, RESET_ARROW, UARROW, ColumnType
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


def _to_python(value):
    return value.item() if hasattr(value, "item") else value


class _EditableColumnName(QLineEdit):
    # The column's name, editable in place like a result-card title: it reads as plain text
    # (frameless) and shows the effective name (the rename, or the original when unchanged).
    # Clicking edits it; committing an empty value (or the original) clears the rename. Tab on an
    # empty field fills the original name so the user can edit from it -- intercepted in event()
    # because the focus framework consumes Tab before keyPressEvent.
    def __init__(self, parent, original, new_name, on_commit):
        super().__init__(parent)
        self._original = original
        self._new_name = new_name or ""
        self._on_commit = on_commit
        self.setFrame(False)
        # Empty (being edited) -> show the Tab hint as placeholder; the original name is filled by Tab.
        self.setPlaceholderText("Tab for original name")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self._refresh_display()

    def _effective(self):
        return self._new_name or self._original

    def _refresh_display(self):
        if not self.hasFocus():
            self.setText(self._effective())
            self.home(False)
        self.setToolTip(self._effective())
        set_stylesheet(
            self,
            css(background="transparent", border="none", padding="0", font_size=Style.FontSize.regular),
        )
        # Bold when the column has been renamed, to signal the change.
        font = self.font()
        font.setBold(bool(self._new_name))
        self.setFont(font)

    def set_new_name(self, new_name):
        self._new_name = new_name or ""
        self._refresh_display()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.setText(self._new_name)  # empty -> placeholder shows the original
        self.selectAll()

    def focusOutEvent(self, event):
        text = self.text().strip()
        self._new_name = "" if text == self._original else text
        super().focusOutEvent(event)
        self._refresh_display()
        self._on_commit(self._new_name)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.clearFocus()
            return
        if key == Qt.Key.Key_Escape:
            self.setText(self._new_name)
            self.clearFocus()
            return
        super().keyPressEvent(event)

    def event(self, e):
        if e.type() == QEvent.Type.KeyPress and e.key() == Qt.Key.Key_Tab and not self.text():
            self.setText(self._original)
            return True
        return super().event(e)


class IISPWACColumnEditor(ItemInSidePanelWithAutoConfig):
    def __init__(self):
        super().__init__()
        self.handler_changed = None
        self.specs = {}  # original_name -> spec dict
        self.unique_values = {}  # original_name -> sorted list of (python) unique values
        self.original_types = {}  # original_name -> the column's original ColumnType value
        self.cards = []  # per-column widget bundles, in column order
        self.order = []  # current column order (original names)
        self._built_columns = None
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

        # Rebuild the cards when the columns change OR when a different study is being configured.
        # Two Preprocess studies over the same data share column names, so without the result-id
        # check switching between them would keep the previous study's widgets (leaking one study's
        # edits into the other's fields).
        if self.order != self._built_columns or result_id != self._built_result_id:
            self._rebuild(columns)
            self._built_columns = list(self.order)
            self._built_result_id = result_id
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
        # The column may already carry a color tag from upstream; keep it unless overridden.
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
            # Keep (checked = keep) comes first, then the editable name, then color / copy / reset.
            keep_checkbox = QCheckBox(card)
            keep_checkbox.setToolTip("Keep this column (uncheck to remove it from the output)")
            keep_checkbox.setChecked(not self.specs[name].get("remove"))
            keep_checkbox.toggled.connect(lambda checked, n=name: self._on_keep(n, checked))
            header.addWidget(keep_checkbox)

            name_field = _EditableColumnName(
                card,
                original=name,
                new_name=self.specs[name]["new_name"],
                on_commit=lambda value, n=name: self._on_rename(n, value),
            )
            header.addWidget(name_field, 1)

            color_btn = QPushButton(card)
            color_btn.setFixedSize(26, 24)
            color_btn.setToolTip("Column color tag (for grouping; e.g. by questionnaire)")
            color_btn.clicked.connect(lambda _=False, n=name: self._open_color_picker(n))
            header.addWidget(color_btn)

            copy_btn = QPushButton(UARROW, card)
            copy_btn.setFixedSize(26, 24)
            if index > 0:
                copy_btn.setToolTip("Copy settings from the column above")
                copy_btn.clicked.connect(lambda _=False, n=name: self._copy_from_above(n))
            else:
                copy_btn.setEnabled(False)
                copy_btn.setToolTip("No column above to copy from")
            header.addWidget(copy_btn)

            reset_btn = QPushButton(RESET_ARROW, card)
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
            body_layout.setSpacing(6)

            # Big, horizontally-aligned actions: Map values + Type on one row (equal width); the
            # Order button (ordinal only) sits half-width below, under Map values.
            grid = QGridLayout()
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(6)
            grid.setVerticalSpacing(6)
            grid.setColumnStretch(0, 1)
            grid.setColumnStretch(1, 1)

            map_button = QPushButton("Map values...", body)
            map_button.clicked.connect(lambda _=False, n=name: self._open_mapping(n))
            grid.addWidget(map_button, 0, 0)

            type_combo = NoScrollComboBox(body)
            type_combo.addItems(_TYPES)
            type_combo.setCurrentText(self.specs[name]["type"])
            type_combo.currentTextChanged.connect(lambda text, n=name: self._on_type(n, text))
            grid.addWidget(type_combo, 0, 1)

            order_button = QPushButton("Order...", body)
            order_button.clicked.connect(lambda _=False, n=name: self._open_order(n))
            grid.addWidget(order_button, 1, 0)  # half-width, aligned under Map values

            body_layout.addLayout(grid)

            body.setEnabled(not self.specs[name].get("remove"))

            self.layout.addWidget(card)
            self.cards.append(
                {
                    "name": name,
                    "card": card,
                    "name_field": name_field,
                    "keep_checkbox": keep_checkbox,
                    "color_button": color_btn,
                    "type_combo": type_combo,
                    "map_button": map_button,
                    "order_button": order_button,
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
            # The Order button appears only for ordinal columns; the action buttons (and the type
            # dropdown) go bold when they carry a change from the default, replacing the old summaries.
            card["order_button"].setVisible(is_ordinal)
            self._style_action_button(card["order_button"], is_ordinal and spec.get("order") is not None)
            self._style_action_button(card["map_button"], self._has_mapping(spec))
            self._style_action_button(card["type_combo"], spec["type"] != self.original_types.get(name))
            self._apply_color_button(name)

    @staticmethod
    def _has_mapping(spec) -> bool:
        return any(f != t for f, t in (spec.get("mapping") or []))

    @staticmethod
    def _style_action_button(button, applied: bool):
        # Bold the label via the widget font (not a stylesheet) when a setting is active, so the
        # button keeps its native pressable look and only changes weight.
        font = button.font()
        font.setBold(applied)
        button.setFont(font)

    def _apply_color_button(self, name):
        card = self._card(name)
        if card is None or card.get("color_button") is None:
            return
        color = self.specs.get(name, {}).get("color")
        button = card["color_button"]
        if isinstance(color, str) and color:
            set_stylesheet(button, css(background=color, border="1px solid gray"))
        else:
            set_stylesheet(
                button, css(background=Style.Color.BackgroundEdit, border=f"1px dashed {Style.Color.BorderElevated}")
            )

    def _changed(self):
        if self._suppress:
            return
        if self.handler_changed:
            self.handler_changed()
        self.on_recalculate()

    def _on_rename(self, name, new_name):
        self.specs[name]["new_name"] = new_name
        self._changed()

    def _on_type(self, name, text):
        self.specs[name]["type"] = text
        self._refresh_all_summaries()
        self._changed()

    def _on_keep(self, name, checked):
        # Checked = keep the column; unchecked = remove it (and gray out its body).
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
            if card.get("name_field") is not None:
                card["name_field"].set_new_name("")
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

    def _open_color_picker(self, name):
        """Pick a pastel color tag for the column (or None to clear)."""

        def choose(color):
            self.specs[name]["color"] = color
            self._apply_color_button(name)
            self._changed()

        show_color_picker(self.widget, choose)

    def _open_order(self, name):
        natural = list(self.unique_values.get(name, []))
        values = self.specs[name]["order"] or natural

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
            css(
                background=Style.Color.Background,
            ),
            css(
                selector="QListWidget::item", background=Style.Color.BackgroundPanel, margin="2px", border_radius="5px"
            ),
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
            # Store a custom order only when it differs from the natural order (else it is "no order").
            self.specs[name]["order"] = ordered if (ordered and ordered != natural) else None
            self._refresh_all_summaries()
            self._changed()

        OverlayPopup(self.widget, content, on_close=on_close)

    def _open_mapping(self, name):
        uniques = self.unique_values.get(name, [])
        existing = {f: t for f, t in (self.specs[name]["mapping"] or [])}

        content = QFrame()
        content.setFixedWidth(600)
        set_stylesheet(
            content, css(background=Style.Color.BackgroundElevated, border=f"1px solid {Style.Color.BorderElevated}")
        )
        outer = QVBoxLayout(content)
        outer.setContentsMargins(12, 12, 12, 12)

        # Long value lists scroll vertically instead of overflowing the screen.
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
            # Tooltips keep the full source/target values readable when truncated.
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
                    target = text  # fall back to the raw string
                mapping.append([value, target])
            # An all-identity mapping is "no mapping".
            if all(f == t for f, t in mapping):
                mapping = None
            self.specs[name]["mapping"] = mapping
            self._refresh_all_summaries()
            self._changed()

        OverlayPopup(self.widget, content, on_close=on_close)

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
