#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

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

# Dropdown entry that means "no correlation target" for a regular column.
_NO_TARGET = "(independent)"


def _default_spec(column_name, role):
    return {
        "column": column_name,
        "role": role,  # "reference" | "driver" | "column"
        "value_source": "existing",
        "custom_values": "",
        "distribution": "empirical",
        "mu": "",
        "sigma": "",
        "target": None,  # column to correlate with (driver -> reference; column -> chosen)
        "coefficient": "",  # desired rank correlation, -1..1 (blank/0 = independent)
    }


class IISPWACBootstrapColumnEditor(ItemInSidePanelWithAutoConfig):
    """Per-column fill configuration for the Bootstrap Sensitivity module. Renders one card
    per selected column, grouped by role (reference, then drivers, then columns). Each card
    chooses how the synthetic rows are filled: the pool of possible values (existing rows vs.
    a user list) and the distribution used to draw from it (empirical, uniform, or normal for
    ordinal/numeric). Drivers and columns also get a correlation row (target + coefficient):
    a driver correlates with the reference; a column correlates with the reference or a
    driver. Rebuilt only when the set of selected columns or their roles changes."""

    def __init__(self):
        super().__init__()
        self.handler_changed = None
        self.specs = {}  # column_name -> spec dict
        self.order = []  # all selected column names, in render order (ref, drivers, columns)
        self.reference = None
        self.drivers = []
        self.regular = []
        self.col_types = {}  # column_name -> ColumnType.value
        self._built_signature = None
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
        regular = list(selector_value[0]) if len(selector_value) > 0 and selector_value[0] else []
        drivers = list(selector_value[1]) if len(selector_value) > 1 and selector_value[1] else []
        reference_list = list(selector_value[2]) if len(selector_value) > 2 and selector_value[2] else []
        saved = kwargs.get(self.name) or []
        saved_by_col = {s["column"]: s for s in saved if isinstance(s, dict) and "column" in s}

        try:
            data = DATA_MANAGER.get_data_from_data_label(data_label=data_label, current_result_id=result_id)
            available = {c.column_name: c.column_type.value for c in data.get_all_columns_as_column_types()}
        except Exception:
            available = {}

        # Keep only columns that still exist, preserving each field's order.
        regular = [c for c in regular if c in available]
        drivers = [c for c in drivers if c in available]
        reference_list = [c for c in reference_list if c in available]
        reference = reference_list[0] if reference_list else None

        self.reference = reference
        self.drivers = drivers
        self.regular = regular
        # Render order: reference first, then drivers, then the regular columns.
        self.order = ([reference] if reference else []) + drivers + regular
        self.col_types = {c: available[c] for c in self.order}

        role_of = {}
        if reference:
            role_of[reference] = "reference"
        for c in drivers:
            role_of[c] = "driver"
        for c in regular:
            role_of[c] = "column"

        # Valid correlation targets for a regular column: the reference and any driver.
        valid_targets = ([reference] if reference else []) + drivers

        specs = {}
        for col in self.order:
            role = role_of[col]
            saved_spec = saved_by_col.get(col)
            spec = _default_spec(col, role)
            if isinstance(saved_spec, dict):
                for key in spec:
                    if key in saved_spec:
                        spec[key] = saved_spec[key]
                spec["column"] = col
                spec["role"] = role
            # A normal distribution is invalid for nominal columns; fall back to empirical.
            if spec["distribution"] == "normal" and available[col] == ColumnType.NOMINAL.value:
                spec["distribution"] = "empirical"
            # Resolve the correlation target per role.
            if role == "reference":
                spec["target"] = None
            elif role == "driver":
                spec["target"] = reference  # drivers always anchor to the reference
            else:  # column
                if spec["target"] not in valid_targets:
                    spec["target"] = None
            specs[col] = spec
        self.specs = specs

        signature = (reference, tuple(drivers), tuple(regular))
        if signature != self._built_signature:
            self._rebuild()
            self._built_signature = signature
        else:
            self._refresh_enabled()

    def get_kwargs(self):
        return {self.name: [self.specs[name] for name in self.order if name in self.specs]}

    # ------------------------------------------------------------------ cards
    def _clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _rebuild(self):
        self._clear_layout()
        self.cards = []

        if not self.order:
            hint = QLabel(
                "Select one or more columns above to configure how the\nsynthetic rows are filled.",
                self.widget,
            )
            set_stylesheet(hint, css(font_size=Style.FontSize.smaller, color=Style.Color.SecondaryText))
            self.layout.addWidget(hint)
            return

        target_options = ([self.reference] if self.reference else []) + self.drivers

        for name in self.order:
            spec = self.specs[name]
            role = spec["role"]
            allow_normal = self.col_types.get(name) in (ColumnType.ORDINAL.value, ColumnType.NUMERIC.value)

            card = QFrame(self.widget)
            set_stylesheet(card, css(border=Style.General.border_elevated))
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(6, 6, 6, 6)
            card_layout.setSpacing(3)

            role_tag = {"reference": " — reference", "driver": " — driver", "column": ""}[role]
            title = QLabel(name + role_tag, card)
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

            # ---- correlation (drivers and columns only) ----
            target_combo = None
            coef_edit = None
            if role in ("driver", "column"):
                corr_row = QWidget(card)
                corr_layout = QHBoxLayout(corr_row)
                corr_layout.setContentsMargins(0, 0, 0, 0)
                corr_layout.addWidget(QLabel("Correlate with:", corr_row))

                if role == "driver":
                    # Drivers always anchor to the reference; show it read-only.
                    target_label = QLabel(self.reference or "(no reference set)", corr_row)
                    set_stylesheet(target_label, css(color=Style.Color.SecondaryText))
                    corr_layout.addWidget(target_label, 1)
                else:
                    target_combo = NoScrollComboBox(corr_row)
                    target_combo.addItems([_NO_TARGET] + target_options)
                    current = spec["target"] if spec["target"] in target_options else _NO_TARGET
                    target_combo.setCurrentText(current)
                    target_combo.currentTextChanged.connect(lambda text, n=name: self._on_target(n, text))
                    corr_layout.addWidget(target_combo, 1)

                corr_layout.addWidget(QLabel("ρ:", corr_row))
                coef_edit = QLineEdit(corr_row)
                coef_edit.setPlaceholderText("0")
                coef_edit.setText(spec["coefficient"])
                coef_edit.editingFinished.connect(lambda n=name, e=coef_edit: self._on_coefficient(n, e))
                corr_layout.addWidget(coef_edit, 1)
                card_layout.addWidget(corr_row)

            self.layout.addWidget(card)
            self.cards.append(
                {
                    "name": name,
                    "card": card,
                    "custom_edit": custom_edit,
                    "normal_row": normal_row,
                    "coef_edit": coef_edit,
                    "target_combo": target_combo,
                }
            )

        self._refresh_enabled()

    def _refresh_enabled(self):
        for card in getattr(self, "cards", []):
            spec = self.specs.get(card["name"])
            if spec is None:
                continue
            card["custom_edit"].setEnabled(spec["value_source"] == "custom")
            card["normal_row"].setVisible(spec["distribution"] == "normal")
            # The coefficient only matters when a target is set.
            if card["coef_edit"] is not None:
                has_target = spec.get("target") is not None
                card["coef_edit"].setEnabled(has_target)

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

    def _on_target(self, name, text):
        self.specs[name]["target"] = None if text == _NO_TARGET else text
        self._refresh_enabled()
        self._changed()

    def _on_coefficient(self, name, edit):
        self.specs[name]["coefficient"] = edit.text().strip()
        self._changed()

    # ------------------------------------------------------------------ misc
    def set_handler_changed(self, handler):
        self.handler_changed = handler

    def set_alert(self):
        pass

    def clear_alert(self):
        for card in getattr(self, "cards", []):
            set_stylesheet(card["card"], css(border=Style.General.border_elevated))
