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


from PySide6.QtCore import QSize
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from src.common.ui_constructor import create_simple_tool_button_qta
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig, ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel


class IISPWACAllocationRows(ItemInSidePanelWithAutoConfig):
    def __init__(self):
        super().__init__()
        self.rows = []

    def post_init(self, name, parent_widget):
        self.name = name
        self.widget = QFrame(parent_widget)
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(5)

        title = QLabel("Allocation:", self.widget)
        self.layout.addWidget(title)

        self.rows_widget = QWidget(self.widget)
        self.rows_layout = QVBoxLayout(self.rows_widget)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(3)
        self.layout.addWidget(self.rows_widget)

        self.add_button = create_simple_tool_button_qta(self.widget, "mdi6.plus", QSize(20, 20))
        self.add_button.setToolTip("Add value")
        self.add_button.clicked.connect(self._add_clicked)
        self.layout.addWidget(self.add_button)
        self.clear_alert()

    def configure(self, **kwargs):
        self.clear_alert()
        rows = kwargs.get(self.name)
        if not rows:
            rows = [{"value": "1", "amount": "remaining"}]
        self._clear_rows()
        for row in rows:
            if not isinstance(row, dict):
                continue
            self._add_row(str(row.get("value", "")), str(row.get("amount", "")), update_remaining=False)
        if not self.rows:
            self._add_row("1", "remaining", update_remaining=False)
        self._update_remaining_row()

    def get_kwargs(self):
        return {
            self.name: [
                {"value": row["value"].text().strip(), "amount": row["amount"].text().strip()} for row in self.rows
            ]
        }

    def set_alert(self):
        set_stylesheet(self.widget, css(border="1px solid red"))

    def clear_alert(self):
        set_stylesheet(self.widget, css(border=Style.General.border_elevated))

    def _add_clicked(self):
        next_value = str(len(self.rows) + 1)
        self._add_row(next_value, "")
        self._update_remaining_row()
        self.on_recalculate()

    def _add_row(self, value, amount, update_remaining=True):
        row_widget = QWidget(self.rows_widget)
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(4)

        value_edit = QLineEdit(row_widget)
        value_edit.setPlaceholderText("Value")
        value_edit.setText(value)
        value_edit.editingFinished.connect(self.on_recalculate)
        row_layout.addWidget(value_edit, 2)

        amount_edit = QLineEdit(row_widget)
        amount_edit.setPlaceholderText("Count / %")
        amount_edit.setText(amount)
        amount_edit.editingFinished.connect(self.on_recalculate)
        row_layout.addWidget(amount_edit, 1)

        remove_button = create_simple_tool_button_qta(row_widget, "mdi6.minus", QSize(18, 18))
        remove_button.setToolTip("Remove value")
        remove_button.clicked.connect(lambda: self._remove_row(row_widget))
        row_layout.addWidget(remove_button)

        self.rows_layout.addWidget(row_widget)
        self.rows.append({"widget": row_widget, "value": value_edit, "amount": amount_edit})
        if update_remaining:
            self._update_remaining_row()

    def _remove_row(self, row_widget):
        self.rows = [row for row in self.rows if row["widget"] is not row_widget]
        row_widget.deleteLater()
        if not self.rows:
            self._add_row("1", "remaining")
        self._update_remaining_row()
        self.on_recalculate()

    def _update_remaining_row(self):
        for index, row in enumerate(self.rows):
            is_last = index == len(self.rows) - 1
            amount = row["amount"]
            amount.blockSignals(True)
            amount.setEnabled(not is_last)
            amount.setReadOnly(is_last)
            if is_last:
                amount.setText("remaining")
                set_stylesheet(
                    amount, css(color=Style.Color.SecondaryText, background_color=Style.Color.BackgroundElevated)
                )
            else:
                if amount.text().strip().lower() == "remaining":
                    amount.setText("")
                set_stylesheet(amount, css(color=Style.Color.Text, background_color=Style.Color.Background))
            amount.blockSignals(False)

    def _clear_rows(self):
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.rows = []


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    spacer = IISPWACSpacer()
    new_name = IISPWACLongTextEdit(label_text="New column name:")
    assignment_mode = IISPWACComboBox(label_text="Assignment mode:", items=["Counts", "Percentages"])
    allocations = IISPWACAllocationRows()


class RandomSubsamples(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Random Sub-samples")
