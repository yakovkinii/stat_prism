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

# VALIDATED

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.common.constant import CROSS, LRARROW, RARROW
from src.pyside_ext.elements.utility.primitive_elements import NoScrollComboBox
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig

# Relationship types offered per row. Label -> semopy operator.
RELATION_REGRESSION = "~"
RELATION_COVARIANCE = "~~"
RELATION_LABELS = {f"predicts ({RARROW})": RELATION_REGRESSION, f"covaries ({LRARROW})": RELATION_COVARIANCE}
_SYMBOL_TO_LABEL = {v: k for k, v in RELATION_LABELS.items()}


def resolve_factor_labels(raw, m) -> list:
    """Latent-factor labels from the comma-separated names field, filled with F1/F2/... -- the same
    rule the SEM main() uses, so the two agree on node names."""
    provided = [part.strip() for part in (raw or "").split(",")]
    labels = []
    for i in range(int(m or 0)):
        custom = provided[i] if i < len(provided) else ""
        labels.append(custom if custom else f"F{i + 1}")
    return labels


class IISPWACPathBuilder(ItemInSidePanelWithAutoConfig):
    def __init__(self, label_text: str = f"Paths (from {RARROW} to):"):
        super().__init__()
        self.label_text = label_text
        self.handler_changed = None
        self.spec = []  # list of {"from": str, "to": str, "type": "~"|"~~"}
        self.nodes = []

    def post_init(self, name, parent_widget):
        self.name = name
        self.widget = QWidget(parent_widget)
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(4)

    def configure(self, **kwargs):
        saved = kwargs.get(self.name)
        self.spec = [dict(p) for p in saved if isinstance(p, dict)] if isinstance(saved, list) else []
        self.nodes = self._compute_nodes(kwargs)
        self._rebuild()

    def _compute_nodes(self, kwargs) -> list:
        """Nodes = the latent factors plus only the observed columns the user assigned as
        indicators in the column selector (not every column in the dataset)."""
        factor_labels = resolve_factor_labels(kwargs.get("factor_names"), kwargs.get("n_factors"))
        observed = []
        for indicators in kwargs.get("column_selector") or []:
            for col in indicators or []:
                if col and col not in observed:
                    observed.append(col)
        return factor_labels + [c for c in observed if c not in factor_labels]

    def get_kwargs(self):
        return {self.name: self.spec}

    def _clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def _rebuild(self):
        self._clear()
        label = QLabel(self.label_text, self.widget)
        set_stylesheet(label, css(font_size=Style.FontSize.smaller, color=Style.Color.SecondaryText))
        self.layout.addWidget(label)

        if not self.nodes:
            hint = QLabel("Assign indicators to your factors first.", self.widget)
            set_stylesheet(hint, css(font_size=Style.FontSize.smaller, color=Style.Color.SecondaryText))
            self.layout.addWidget(hint)
            return

        for index, path in enumerate(self.spec):
            self.layout.addWidget(self._path_row(index, path))

        add_button = QPushButton("+ Add path", self.widget)
        add_button.clicked.connect(self._add_path)
        self.layout.addWidget(add_button)

    def _path_row(self, index, path) -> QWidget:
        row_widget = QFrame(self.widget)
        set_stylesheet(row_widget, css(border=Style.General.border_elevated))
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(4, 4, 4, 4)
        row.setSpacing(4)

        from_combo = self._node_combo(path, "from", self.nodes[0])
        from_combo.currentTextChanged.connect(lambda text, i=index: self._set(i, "from", text))
        row.addWidget(from_combo, 1)

        type_combo = NoScrollComboBox(row_widget)
        type_combo.addItems(list(RELATION_LABELS.keys()))
        type_combo.setCurrentText(_SYMBOL_TO_LABEL.get(path.get("type"), next(iter(RELATION_LABELS))))
        path["type"] = RELATION_LABELS[type_combo.currentText()]
        type_combo.currentTextChanged.connect(lambda text, i=index: self._set(i, "type", RELATION_LABELS.get(text)))
        row.addWidget(type_combo)

        to_combo = self._node_combo(path, "to", self.nodes[-1])
        to_combo.currentTextChanged.connect(lambda text, i=index: self._set(i, "to", text))
        row.addWidget(to_combo, 1)

        remove_button = QPushButton(CROSS, row_widget)
        remove_button.setFixedSize(24, 24)
        remove_button.clicked.connect(lambda _, i=index: self._remove_path(i))
        row.addWidget(remove_button)
        return row_widget

    def _node_combo(self, path, key, default):
        combo = NoScrollComboBox(self.widget)
        combo.addItems(self.nodes)
        current = path.get(key) if path.get(key) in self.nodes else default
        combo.setCurrentText(current)
        path[key] = current
        return combo

    def _changed(self):
        if self.handler_changed:
            self.handler_changed()
        self.on_recalculate()

    def _add_path(self):
        self.spec.append({"from": self.nodes[0], "to": self.nodes[-1], "type": RELATION_REGRESSION})
        self._rebuild()
        self._changed()

    def _remove_path(self, index):
        if 0 <= index < len(self.spec):
            self.spec.pop(index)
            self._rebuild()
            self._changed()

    def _set(self, index, key, value):
        if 0 <= index < len(self.spec) and value is not None:
            self.spec[index][key] = value
            self._changed()

    def set_handler_changed(self, handler):
        self.handler_changed = handler

    def set_alert(self):
        set_stylesheet(self.widget, css(border="1px solid red"))

    def clear_alert(self):
        set_stylesheet(self.widget, css(border="none"))
