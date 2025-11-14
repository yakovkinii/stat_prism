#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QLabel, QDoubleSpinBox, QPushButton, QGridLayout, \
    QDialog

from src.common.constant import SettingsPanelSize
from src.common.decorators import log_method_noarg
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.layout import HBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACFlip(ItemInSidePanelWithAutoConfig):
    def __init__(self):
        super().__init__()
        self.handler_state_changed = None
        self.recalculate_reference_when_able = True
        self.column = None
        self.column_name = None

    def post_init(self, name, parent_widget):
        self.name = name

        self.widget, self.layout = add_widget(
            parent=parent_widget,
            inner_layout_class=HBoxLayout,
        )
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.check, _ = add_widget(parent=self.widget, outer_layout=self.layout, widget=QCheckBox(parent_widget))
        self.check.setText("Flip")
        self.check.stateChanged.connect(self.on_state_changed)

        self.spinbox, _ = add_widget(
            parent=self.widget,
            outer_layout=self.layout,
            widget_class=QDoubleSpinBox,
        )
        self.spinbox.setRange(-999999.0, 999999.0)
        self.spinbox.setDecimals(2)
        self.spinbox.setSingleStep(1.0)
        self.spinbox.valueChanged.connect(self.on_state_changed)

        self.view_button, _ = add_widget(
            parent=self.widget,
            outer_layout=self.layout,
            widget_class=QPushButton,
        )
        self.view_button.setText("Preview")
        self.view_button.clicked.connect(self.on_view_clicked)

        self.clear_alert()

    def get_kwargs(self):
        return {
            self.name: {
                "flip": self.check.isChecked(),
                "reference_value": self._get_reference_value(),
            }
        }

    def configure(self, **kwargs):
        state = kwargs[self.name]
        self.update_column(**kwargs)
        if state is None:
            state = {
                "flip": False,
                "reference_value": None,
            }

        if self.recalculate_reference_when_able:
            state["reference_value"] = self.get_default_reference_value()

        self.check.setChecked(state["flip"])
        self.spinbox.setValue(state["reference_value"])
        self.spinbox.setEnabled(state["flip"])
        self.view_button.setEnabled(state["flip"])

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

            name = kwargs["column_selector"][0][0]
            self.column = data[name].data_series
            if self.column_name != data[name].column_name:
                self.recalculate_reference_when_able = True
            self.column_name = data[name].column_name
        except Exception as e:
            self.column = None
            self.column_name = None

    def get_default_reference_value(self) -> float:
        if self.column is None:
            self.recalculate_reference_when_able = True
            return 0.0
        self.recalculate_reference_when_able = False
        return self.column.max() + self.column.min()

    @log_method_noarg
    def set_alert(self):
        set_stylesheet(self.widget, css(border="1px solid red"))

    @log_method_noarg
    def clear_alert(self):
        # set color to checkbox itself
        set_stylesheet(self.widget, css(border="none"))

    @log_method_noarg
    def on_state_changed(self):
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
        unique_values = sorted(self.column.unique())
        reference_value = self._get_reference_value()

        self.v_widget, self.layout_for_values = add_widget(
            widget=QDialog(self.widget),
            outer_layout=self.layout,
            inner_layout_class=QGridLayout,
        )
        self.v_widget.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.v_widget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.v_widget.setWindowTitle("Flip Preview")
        self.v_widget.setMinimumWidth(SettingsPanelSize.popup_minimum_width)

        for i, value in enumerate(unique_values):
            label_left = QLabel(self.v_widget)
            label_left.setText(str(value))
            label_left.setFont(Style.font_regular)
            label_left.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            label_center = QLabel(self.v_widget)
            icon = qta.icon("mdi.arrow-right", color="black")
            label_center.setPixmap(icon.pixmap(20, 20))
            label_center.setFixedWidth(20)

            label_right = QLabel(self.v_widget)
            label_right.setText(str(reference_value - value))
            label_right.setFont(Style.font_regular)
            label_right.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)


            self.layout_for_values.addWidget(label_left, i, 0)
            self.layout_for_values.addWidget(label_center, i, 1)
            self.layout_for_values.addWidget(label_right, i, 2)

        self.v_widget.exec()