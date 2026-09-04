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


from PySide6.QtWidgets import QCheckBox, QLabel, QVBoxLayout, QWidget

from src.common.constant import RARROW
from src.common.decorators import log_method_noarg
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig
from src.side_area_panel.modules.common.result.registry import RESULTS


class IISPWACCrossLoadingList(ItemInSidePanelWithAutoConfig):
    def __init__(self, label_text="Apply cross-loadings:"):
        super().__init__()
        self.label_text = label_text
        self.pairs = []  # list of ((item, factor_index), QCheckBox)

    def post_init(self, name, parent_widget):
        self.name = name
        self.widget = QWidget(parent_widget)
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(3)
        set_stylesheet(self.widget, css(border=Style.General.border_elevated))
        self.label = QLabel(self.label_text, self.widget)
        self.layout.addWidget(self.label)
        self.container = QWidget(self.widget)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(2)
        self.layout.addWidget(self.container)
        self.clear_alert()

    def configure(self, **kwargs):
        approved = [tuple(p) for p in (kwargs.get(self.name) or []) if isinstance(p, (list, tuple)) and len(p) == 2]
        approved_keys = {(str(item), int(fi)) for item, fi in approved}

        suggestions = []
        total_suggestions = None
        result_id = kwargs.get("result_id")
        try:
            suggestions = getattr(RESULTS[result_id], "suggested_cross_loadings", None) or []
            total_suggestions = getattr(RESULTS[result_id], "suggested_cross_loadings_total", None)
        except Exception:
            suggestions = []

        # Candidates: already-applied first (so they stay checked/visible), then new suggestions.
        # Each entry: (item, factor_index, score_or_None).
        candidates = [(str(item), int(fi), None) for item, fi in approved]
        seen = set(approved_keys)
        for item, fi, score in suggestions:
            key = (str(item), int(fi))
            if key not in seen:
                candidates.append((key[0], key[1], score))
                seen.add(key)

        self._clear_container()
        self.pairs = []
        # Show the full suggestion count (e.g. "(54)") even though only the top few are listed.
        shown = total_suggestions if total_suggestions is not None else len(candidates)
        self.label.setText(f"{self.label_text} ({shown})")
        for item, fi, score in candidates:
            text = f"{item} {RARROW} F{fi + 1}" + (f"  (r={score:.2f})" if score is not None else "")
            checkbox = QCheckBox(text, self.container)
            checkbox.setToolTip(text)
            checkbox.setChecked((item, fi) in approved_keys)
            checkbox.stateChanged.connect(self.on_changed)
            self.container_layout.addWidget(checkbox)
            self.pairs.append(((item, fi), checkbox))

    def _clear_container(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def get_kwargs(self):
        # Applied (checked) cross-loadings as [item, factor_index] pairs.
        return {self.name: [[item, fi] for (item, fi), checkbox in self.pairs if checkbox.isChecked()]}

    @log_method_noarg
    def set_alert(self):
        set_stylesheet(self.widget, css(border="1px solid red"))

    @log_method_noarg
    def clear_alert(self):
        set_stylesheet(self.widget, css(border=Style.General.border_elevated))

    def on_changed(self, *args):
        self.on_recalculate()
