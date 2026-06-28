#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""A dynamic "Remove:" list of per-ID checkboxes for row-removal steps.

A ``detector`` callback (passed in by each module) turns the current settings + data into
an ordered list of candidate row IDs proposed for removal. This element shows one checkbox
per candidate, all ticked by default; the user can untick any to *keep* that respondent.

The saved value is the list of *unchecked* (kept) IDs, so newly detected outliers always
default to "remove". main() reruns the same detector and drops every candidate except the
kept ones (see ``modules/common/removal.finalize_removal``).

It rebuilds itself in ``configure``, which the panel reruns after every recalculation, so
the candidate list always reflects the latest column / method selection.
"""

from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.common.decorators import log_method_noarg
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACRemoveList(ItemInSidePanelWithAutoConfig):
    def __init__(self, detector, label_text="Remove:"):
        super().__init__()
        # detector(data, params_dict) -> ordered list of candidate IDs to remove.
        self.detector = detector
        self.label_text = label_text
        self.pairs = []  # list of (id_value, QCheckBox)

    def post_init(self, name, parent_widget):
        self.name = name

        self.widget = QWidget(parent_widget)
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        set_stylesheet(self.widget, css(border=Style.General.border_elevated))

        header = QWidget(self.widget)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        self.label = QLabel(self.label_text, header)
        header_layout.addWidget(self.label)
        header_layout.addStretch()
        self.all_button = QPushButton("All", header)
        self.none_button = QPushButton("None", header)
        for button in (self.all_button, self.none_button):
            button.setFixedHeight(24)
            header_layout.addWidget(button)
        self.all_button.clicked.connect(lambda: self._set_all(True))
        self.none_button.clicked.connect(lambda: self._set_all(False))
        self.layout.addWidget(header)

        self.container = QWidget(self.widget)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(3)
        self.layout.addWidget(self.container)

        self.clear_alert()

    def configure(self, **kwargs):
        spec = kwargs.get(self.name)
        kept_set = set(spec) if spec else set()

        self._clear_container()
        self.pairs = []

        candidates = []
        data_label = kwargs.get("data_source") or "Auto"
        result_id = kwargs.get("result_id")
        try:
            data = DATA_MANAGER.get_data_from_data_label(data_label=data_label, current_result_id=result_id)
            candidates = self.detector(data, kwargs) or []
        except Exception:
            candidates = []

        self.label.setText(f"{self.label_text} ({len(candidates)} detected)")
        self._toggle_buttons_enabled(bool(candidates))

        for id_value in candidates:
            checkbox = QCheckBox(str(id_value), self.container)
            checkbox.setToolTip(str(id_value))
            checkbox.setChecked(id_value not in kept_set)
            checkbox.stateChanged.connect(self.on_changed)
            self.container_layout.addWidget(checkbox)
            self.pairs.append((id_value, checkbox))

    def _clear_container(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _toggle_buttons_enabled(self, enabled):
        self.all_button.setEnabled(enabled)
        self.none_button.setEnabled(enabled)

    def _set_all(self, checked):
        if not self.pairs:
            return
        for _, checkbox in self.pairs:
            checkbox.blockSignals(True)
            checkbox.setChecked(checked)
            checkbox.blockSignals(False)
        self.on_changed()

    def get_kwargs(self):
        # Persist the unchecked (kept) IDs, so new detections default to "remove".
        return {self.name: [id_value for id_value, checkbox in self.pairs if not checkbox.isChecked()]}

    @log_method_noarg
    def set_alert(self):
        set_stylesheet(self.widget, css(border="1px solid red"))

    @log_method_noarg
    def clear_alert(self):
        set_stylesheet(self.widget, css(border=Style.General.border_elevated))

    def on_changed(self, *args):
        self.on_recalculate()
