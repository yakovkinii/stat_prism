#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from src.common.constant import ColumnType
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.utility.primitive_elements import NoScrollComboBox
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig

# (spec key, label) pairs for the two combos. The stored spec value is the key.
VALUE_SOURCES = [("existing", "From existing rows"), ("custom", "Custom list (comma-sep)")]
DISTRIBUTIONS = [("empirical", "Empirical (match existing)"), ("uniform", "Uniform")]
# Normal is only offered for ordinal / numeric columns.
DISTRIBUTION_NORMAL = ("normal", "Normal (μ, σ)")

_SOURCE_LABEL = {key: label for key, label in VALUE_SOURCES}
_SOURCE_KEY = {label: key for key, label in VALUE_SOURCES}
_DIST_LABEL = {key: label for key, label in [*DISTRIBUTIONS, DISTRIBUTION_NORMAL]}
_DIST_KEY = {label: key for key, label in [*DISTRIBUTIONS, DISTRIBUTION_NORMAL]}


def _default_spec(column_name):
    return {
        "column": column_name,
        "value_source": "existing",
        "custom_values": "",
        "distribution": "empirical",
        "mu": "",
        "sigma": "",
    }


class IISPWACBootstrapColumnEditor(ItemInSidePanelWithAutoConfig):
    """Per-column fill configuration for the Bootstrap Sensitivity module. Renders one
    card per *selected* column (read from the sibling column selector's value), each
    choosing how the synthetic rows are filled: the pool of possible values (existing
    rows vs. a user list) and the distribution used to draw from it (empirical, uniform,
    or normal for ordinal/numeric). Rebuilt only when the selected-column set changes."""

    def __init__(self):
        super().__init__()
        self.handler_changed = None
        self.specs = {}  # column_name -> spec dict
        self.order = []  # currently-selected column names, in order
        self.col_types = {}  # column_name -> ColumnType.value
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
        selector_value = kwargs.get("column_selector") or []
        selected = list(selector_value[0]) if selector_value else []
        saved = kwargs.get(self.name) or []
        saved_by_col = {s["column"]: s for s in saved if isinstance(s, dict) and "column" in s}

        try:
            data = DATA_MANAGER.get_data_from_data_label(data_label=data_label, current_result_id=result_id)
            available = {c.column_name: c.column_type.value for c in data.get_all_columns_as_column_types()}
        except Exception:
            available = {}

        # Keep only columns that still exist, preserving the selector's order.
        selected = [c for c in selected if c in available]
        self.order = selected
        self.col_types = {c: available[c] for c in selected}

        specs = {}
        for col in selected:
            saved_spec = saved_by_col.get(col)
            spec = _default_spec(col)
            if isinstance(saved_spec, dict):
                spec.update({k: saved_spec.get(k, spec[k]) for k in spec})
                spec["column"] = col
            # A normal distribution is invalid for nominal columns; fall back to empirical.
            if spec["distribution"] == "normal" and available[col] == ColumnType.NOMINAL.value:
                spec["distribution"] = "empirical"
            specs[col] = spec
        self.specs = specs

        if self.order != self._built_columns:
            self._rebuild()
            self._built_columns = list(self.order)
        else:
            self._refresh_enabled()

    def get_kwargs(self):
        return {self.name: [self.specs[name] for name in self.order if name in self.specs]}

    # ------------------------------------------------------------------ cards
    def _rebuild(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.cards = []

        if not self.order:
            hint = QLabel("Select one or more columns above to configure how the\nsynthetic rows are filled.", self.widget)
            set_stylesheet(hint, css(font_size=Style.FontSize.smaller, color=Style.Color.SecondaryText))
            self.layout.addWidget(hint)
            return

        for name in self.order:
            allow_normal = self.col_types.get(name) in (ColumnType.ORDINAL.value, ColumnType.NUMERIC.value)
            spec = self.specs[name]

            card = QFrame(self.widget)
            set_stylesheet(card, css(border=Style.General.border_elevated))
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(6, 6, 6, 6)
            card_layout.setSpacing(3)

            title = QLabel(name, card)
            title.setToolTip(f"{name} ({self.col_types.get(name, '')})")
            set_stylesheet(title, css(font_size=Style.FontSize.regular))
            card_layout.addWidget(title)

            # ---- value source ----
            source_row = QHBoxLayout()
            source_row.addWidget(QLabel("Values:", card))
            source_combo = NoScrollComboBox(card)
            source_combo.addItems([label for _, label in VALUE_SOURCES])
            source_combo.setCurrentText(_SOURCE_LABEL.get(spec["value_source"], VALUE_SOURCES[0][1]))
            source_combo.currentTextChanged.connect(lambda text, n=name: self._on_source(n, text))
            source_row.addWidget(source_combo, 1)
            card_layout.addLayout(source_row)

            custom_edit = QLineEdit(card)
            custom_edit.setPlaceholderText("Comma-separated values, e.g. 1, 2, 3")
            custom_edit.setText(spec["custom_values"])
            custom_edit.editingFinished.connect(lambda n=name, e=custom_edit: self._on_custom(n, e))
            card_layout.addWidget(custom_edit)

            # ---- distribution ----
            dist_row = QHBoxLayout()
            dist_row.addWidget(QLabel("Draw:", card))
            dist_combo = NoScrollComboBox(card)
            dist_labels = [label for _, label in DISTRIBUTIONS]
            if allow_normal:
                dist_labels.append(DISTRIBUTION_NORMAL[1])
            dist_combo.addItems(dist_labels)
            dist_combo.setCurrentText(_DIST_LABEL.get(spec["distribution"], DISTRIBUTIONS[0][1]))
            dist_combo.currentTextChanged.connect(lambda text, n=name: self._on_dist(n, text))
            dist_row.addWidget(dist_combo, 1)
            card_layout.addLayout(dist_row)

            normal_row = QWidget(card)
            normal_layout = QHBoxLayout(normal_row)
            normal_layout.setContentsMargins(0, 0, 0, 0)
            normal_layout.addWidget(QLabel("μ:", normal_row))
            mu_edit = QLineEdit(normal_row)
            mu_edit.setPlaceholderText("auto")
            mu_edit.setText(spec["mu"])
            mu_edit.editingFinished.connect(lambda n=name, e=mu_edit: self._on_mu(n, e))
            normal_layout.addWidget(mu_edit, 1)
            normal_layout.addWidget(QLabel("σ:", normal_row))
            sigma_edit = QLineEdit(normal_row)
            sigma_edit.setPlaceholderText("auto")
            sigma_edit.setText(spec["sigma"])
            sigma_edit.editingFinished.connect(lambda n=name, e=sigma_edit: self._on_sigma(n, e))
            normal_layout.addWidget(sigma_edit, 1)
            card_layout.addWidget(normal_row)

            self.layout.addWidget(card)
            self.cards.append(
                {
                    "name": name,
                    "card": card,
                    "custom_edit": custom_edit,
                    "normal_row": normal_row,
                }
            )

        self._refresh_enabled()

    def _card(self, name):
        for card in getattr(self, "cards", []):
            if card["name"] == name:
                return card
        return None

    def _refresh_enabled(self):
        for card in getattr(self, "cards", []):
            spec = self.specs.get(card["name"])
            if spec is None:
                continue
            card["custom_edit"].setEnabled(spec["value_source"] == "custom")
            card["normal_row"].setVisible(spec["distribution"] == "normal")

    # ------------------------------------------------------------------ events
    def _changed(self):
        if self._suppress:
            return
        if self.handler_changed:
            self.handler_changed()
        self.on_recalculate()

    def _on_source(self, name, text):
        self.specs[name]["value_source"] = _SOURCE_KEY.get(text, "existing")
        self._refresh_enabled()
        self._changed()

    def _on_custom(self, name, edit):
        self.specs[name]["custom_values"] = edit.text().strip()
        self._changed()

    def _on_dist(self, name, text):
        self.specs[name]["distribution"] = _DIST_KEY.get(text, "empirical")
        self._refresh_enabled()
        self._changed()

    def _on_mu(self, name, edit):
        self.specs[name]["mu"] = edit.text().strip()
        self._changed()

    def _on_sigma(self, name, edit):
        self.specs[name]["sigma"] = edit.text().strip()
        self._changed()

    # ------------------------------------------------------------------ misc
    def set_handler_changed(self, handler):
        self.handler_changed = handler

    def set_alert(self):
        pass

    def clear_alert(self):
        for card in getattr(self, "cards", []):
            set_stylesheet(card["card"], css(border=Style.General.border_elevated))
