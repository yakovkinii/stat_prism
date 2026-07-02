#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import pandas as pd
from PySide6.QtWidgets import QCheckBox, QDoubleSpinBox, QPushButton

from src.common.decorators import log_method_noarg
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.layout import HBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.overlay_popup import show_value_mapping_popup
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACReference(ItemInSidePanelWithAutoConfig):
    """A reference value, auto-inferred as (max + min) over the pooled selected
    columns. The "Manual" checkbox (off by default) switches to a manual override;
    editing the value engages manual mode automatically.

    get_kwargs returns None while auto (the module's main() then computes the
    reference from live data, avoiding any stale-value lag) or the number while
    manual.
    """

    def __init__(self, label_text: str = "Manual", field_index: int = 0):
        super().__init__()
        self.label_text = label_text
        # Which column_selector field to pool for the auto value / preview (0 by default;
        # modules with more than one field, e.g. Calculate Scale, point this at the right one).
        self.field_index = field_index
        self.handler_state_changed = None
        # Pooled numeric values of all selected columns (for the auto value / preview).
        self.column = None
        self._programmatic = False

    def post_init(self, name, parent_widget):
        self.name = name

        self.widget, self.layout = add_widget(
            parent=parent_widget,
            inner_layout_class=HBoxLayout,
        )
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.check, _ = add_widget(parent=self.widget, outer_layout=self.layout, widget=QCheckBox(parent_widget))
        self.check.setText(self.label_text)
        self.check.stateChanged.connect(self.on_check_changed)

        self.spinbox, _ = add_widget(
            parent=self.widget,
            outer_layout=self.layout,
            widget_class=QDoubleSpinBox,
        )
        self.spinbox.setRange(-999999.0, 999999.0)
        self.spinbox.setDecimals(2)
        self.spinbox.setSingleStep(1.0)
        self.spinbox.valueChanged.connect(self.on_spinbox_changed)

        self.view_button, _ = add_widget(
            parent=self.widget,
            outer_layout=self.layout,
            widget_class=QPushButton,
        )
        self.view_button.setText("Preview")
        self.view_button.clicked.connect(self.on_view_clicked)

        self.clear_alert()

    def get_kwargs(self):
        return {self.name: self._get_reference_value() if self.check.isChecked() else None}

    def configure(self, **kwargs):
        self.update_column(**kwargs)
        state = kwargs[self.name]
        manual = state is not None
        reference = state if manual else self.get_default_reference_value()

        self._programmatic = True
        self.check.setChecked(manual)
        self.spinbox.setValue(reference if reference is not None else 0.0)
        self._programmatic = False

    def update_column(self, **kwargs):
        try:
            assert "data_source" in kwargs
            data_label = kwargs["data_source"]
            if data_label is None:
                data_label = "Auto"
            result_id = kwargs["result_id"]

            data = DATA_MANAGER.get_data_from_data_label(
                data_label=data_label,
                current_result_id=result_id,
            )

            selector = kwargs["column_selector"]
            names = selector[self.field_index] if len(selector) > self.field_index else None
            if not names:
                raise ValueError("No columns selected")
            # Pool all selected columns so they share one min/max reference.
            self.column = pd.concat(
                [pd.to_numeric(data[name].data_series, errors="coerce") for name in names],
                ignore_index=True,
            )
        except Exception:
            self.column = None

    def get_default_reference_value(self) -> float:
        if self.column is None or self.column.dropna().empty:
            return 0.0
        return self.column.max() + self.column.min()

    @log_method_noarg
    def set_alert(self):
        set_stylesheet(self.widget, css(border="1px solid red"))

    @log_method_noarg
    def clear_alert(self):
        set_stylesheet(self.widget, css(border="none"))

    @log_method_noarg
    def on_check_changed(self):
        if self._programmatic:
            return
        if self.handler_state_changed:
            self.handler_state_changed()
        self.on_recalculate()

    @log_method_noarg
    def on_spinbox_changed(self):
        if self._programmatic:
            return
        # Editing the value engages the manual override automatically.
        if not self.check.isChecked():
            self._programmatic = True
            self.check.setChecked(True)
            self._programmatic = False
        if self.handler_state_changed:
            self.handler_state_changed()
        self.on_recalculate()

    def set_handler_state_changed(self, handler):
        self.handler_state_changed = handler

    def _get_reference_value(self):
        value = self.spinbox.value()
        if int(value) == value:
            return int(value)
        return value

    def on_view_clicked(self):
        if self.column is None:
            return
        unique_values = sorted(self.column.dropna().unique())
        self.v_widget = show_value_mapping_popup(self.view_button, unique_values, self._get_reference_value())
