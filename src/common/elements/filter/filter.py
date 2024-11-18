#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

import logging
from enum import Enum
from typing import List

import attrs
import qtawesome as qta
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from src.common.elements.base.base import BasePanelElement
from src.common.elements.utility.layout_helpers import empty_widget, widget_in_layout
from src.common.elements.utility.primitive_elements import QLabelClickable
from src.common.messages import Message, MessageType
from src.common.size import Font
from src.common.unique_qss import set_stylesheet

RESPONDENT_NUMBER = "[respondent #]"


class FilterTypeRemoveKeep(Enum):
    REMOVE = "Remove"
    KEEP = "Keep only"


class FilterTypeOperation(Enum):
    EQUAL = "equal to (==)"
    GREATER = "greater than (>)"
    LESS = "less than (<)"
    GREATER_EQUAL = "greater or equal than (>=)"
    LESS_EQUAL = "less or equal than (<=)"
    CONTAINS = "in (comma-delimited)"


FILTER_TYPE_OPERATION_MAPPING_OPERATOR = {
    FilterTypeOperation.EQUAL: "==",
    FilterTypeOperation.GREATER: ">",
    FilterTypeOperation.LESS: "<",
    FilterTypeOperation.GREATER_EQUAL: ">=",
    FilterTypeOperation.LESS_EQUAL: "<=",
    FilterTypeOperation.CONTAINS: "in",
}

FILTER_TYPE_OPERATION_MAPPING_VERBAL = {
    FilterTypeOperation.EQUAL: "equal to",
    FilterTypeOperation.GREATER: "greater than",
    FilterTypeOperation.LESS: "less than",
    FilterTypeOperation.GREATER_EQUAL: "greater or equal than",
    FilterTypeOperation.LESS_EQUAL: "less or equal than",
    FilterTypeOperation.CONTAINS: "in",
}


@attrs.define
class FilterSettings:
    column_name: str
    filter_type_remove_keep: FilterTypeRemoveKeep
    filter_type_operation: FilterTypeOperation
    filter_value: any

    def get_query(self):
        if self.column_name == RESPONDENT_NUMBER:
            column_name = "index"
        else:
            column_name = self.column_name

        filter_value = self.filter_value
        if self.filter_type_operation == FilterTypeOperation.CONTAINS:
            filter_value = f"[{filter_value}]"
        query = f"`{column_name}` {FILTER_TYPE_OPERATION_MAPPING_OPERATOR[self.filter_type_operation]} {filter_value}"
        if self.filter_type_remove_keep == FilterTypeRemoveKeep.REMOVE:
            return f"~({query})"
        else:
            return query

    def get_text(self):
        return (
            f"{self.filter_type_remove_keep.value} respondents with {self.column_name} "
            f"{FILTER_TYPE_OPERATION_MAPPING_VERBAL[self.filter_type_operation]} {self.filter_value}"
        )


class FilterSetup(BasePanelElement):
    def __init__(self):
        super().__init__()

    def setup(self):
        self.already_filtered_rows = None
        self.configuring = True
        self.dtypes = None
        self.column_names = None
        self.df = None
        self.filter_settings = None
        self.widget = QWidget(self.parent_widget)
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)
        self.widget.setLayout(self.layout)
        set_stylesheet(self.widget, f"#id{{border: 1px solid #aaa;}}")

        self.label = widget_in_layout(
            widget=QLabel(self.widget),
            layout=self.layout,
            setup=lambda widget, layout: [
                widget.setText("Add New Filter"),
                set_stylesheet(widget, f"#id{{font-size: {Font.size_big}px; color: grey;}}"),
                widget.setAlignment(Qt.AlignmentFlag.AlignCenter),
            ],
        )

        w1, l1 = empty_widget(
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QHBoxLayout,
        )

        self.filter_type_remove_keep = widget_in_layout(
            widget=QComboBox(w1),
            layout=l1,
            setup=lambda widget, layout: [
                widget.addItem(FilterTypeRemoveKeep.REMOVE.value),
                widget.addItem(FilterTypeRemoveKeep.KEEP.value),
                widget.currentIndexChanged.connect(self.filter_changed),
            ],
        )
        _ = widget_in_layout(
            widget=QLabel(w1),
            layout=l1,
            setup=lambda widget, layout: [
                widget.setText(" respondents with"),
                set_stylesheet(widget, f"font-size: {Font.size}px;"),
            ],
        )
        l1.addStretch()

        self.filter_column = widget_in_layout(
            widget=QComboBox(self.widget),
            layout=self.layout,
            setup=lambda widget, layout: [
                widget.currentIndexChanged.connect(self.filter_column_changed),
                widget.currentIndexChanged.connect(self.filter_changed),
            ],
        )

        self.filter_type_operation = widget_in_layout(
            widget=QComboBox(self.widget),
            layout=self.layout,
            setup=lambda widget, layout: [
                widget.addItem(FilterTypeOperation.EQUAL.value),
                widget.addItem(FilterTypeOperation.GREATER.value),
                widget.addItem(FilterTypeOperation.LESS.value),
                widget.addItem(FilterTypeOperation.GREATER_EQUAL.value),
                widget.addItem(FilterTypeOperation.LESS_EQUAL.value),
                widget.addItem(FilterTypeOperation.CONTAINS.value),
                widget.currentIndexChanged.connect(self.filter_changed),
            ],
        )

        self.filter_value = widget_in_layout(
            widget=QLineEdit(self.widget),
            layout=self.layout,
            setup=lambda widget, layout: [widget.textChanged.connect(self.filter_changed)],
        )

        w2, l2 = empty_widget(
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QHBoxLayout,
        )
        self.result_label = widget_in_layout(
            widget=QLabel(w2),
            layout=l2,
            setup=lambda widget, layout: [
                set_stylesheet(widget, f"font-size: {Font.size}px;"),
                widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse),
            ],
        )

        self.clear_button = widget_in_layout(
            widget=QPushButton(w2),
            layout=l2,
            setup=lambda widget, layout: [
                widget.setText(""),
                widget.setIcon(qta.icon("fa5s.times")),
                widget.setIconSize(QtCore.QSize(24, 24)),
                widget.setFixedWidth(32),
                widget.setFixedHeight(32),
                widget.setEnabled(True),
                widget.clicked.connect(self.clear),
            ],
        )

        self.ok_button = widget_in_layout(
            widget=QPushButton(w2),
            layout=l2,
            setup=lambda widget, layout: [
                widget.setText(""),
                widget.setIcon(qta.icon("fa5s.check")),
                widget.setIconSize(QtCore.QSize(24, 24)),
                widget.setFixedWidth(32),
                widget.setFixedHeight(32),
                widget.setEnabled(False),
                widget.clicked.connect(
                    lambda: self.handler(
                        Message(
                            message_type=MessageType.FILTER_ADDED,
                            payload=self.filter_settings,
                            caller_id=self.element_id,
                        )
                    )
                ),
            ],
        )

    def configure(
        self, root_class, df, column_names, dtypes, already_filtered_rows, filter_settings: FilterSettings = None
    ):
        self.root_class = root_class
        self.configuring = True
        self.already_filtered_rows = already_filtered_rows
        self.df = df.query(f"index not in {already_filtered_rows}")
        self.column_names = column_names
        self.dtypes = dtypes
        self.filter_settings = filter_settings

        self.filter_column.clear()
        if RESPONDENT_NUMBER in column_names:
            logging.error(f"Column names contain {RESPONDENT_NUMBER}")
        else:
            self.filter_column.addItem(RESPONDENT_NUMBER)
        self.filter_column.addItems(column_names)

        if filter_settings is not None:
            self.filter_column.setCurrentText(filter_settings.column_name)
            self.filter_type_remove_keep.setCurrentText(filter_settings.filter_type_remove_keep.value)
            self.filter_type_operation.setCurrentText(filter_settings.filter_type_operation.value)
            self.filter_value.setText(filter_settings.filter_value)
            self.configuring = False
            self.filter_changed()
        else:
            self.filter_column.setCurrentIndex(0)
            self.filter_type_operation.setCurrentIndex(0)
            self.filter_value.setText("")
            self.result_label.setText("")
            self.ok_button.setEnabled(False)
            self.configuring = False

    def filter_column_changed(self):
        if self.configuring:
            return
        new_column = self.filter_column.currentText()
        if new_column == "[respondent #]":
            column_dtype = "int"
        else:
            column_dtype = self.dtypes[self.column_names.index(new_column)]
        if column_dtype not in ["int", "float"]:
            model = self.filter_type_operation.model()
            for index in [1, 2, 3, 4]:
                model.item(index).setFlags(model.item(index).flags() & ~Qt.ItemFlag.ItemIsEnabled)
            if self.filter_type_operation.currentText() in [
                FilterTypeOperation.GREATER.value,
                FilterTypeOperation.LESS.value,
                FilterTypeOperation.GREATER_EQUAL.value,
                FilterTypeOperation.LESS_EQUAL.value,
            ]:
                self.filter_type_operation.setCurrentIndex(0)
        else:
            model = self.filter_type_operation.model()
            for index in [1, 2, 3, 4]:
                model.item(index).setFlags(model.item(index).flags() | Qt.ItemFlag.ItemIsEnabled)

    def filter_changed(self):
        if self.configuring:
            return
        if self.filter_value.text() == "":
            self.ok_button.setEnabled(False)
            self.root_class.data_panel.tabledata.filtered_rows = self.already_filtered_rows
            self.root_class.data_panel.tabledata.data_changed()

            try:
                if self.filter_column.currentText() == RESPONDENT_NUMBER:
                    self.result_label.setText("Example: 0")
                    return

                unique_values = self.df[self.filter_column.currentText()].unique()

                def format_value(val):
                    if isinstance(val, str):
                        return f'"{val}"'
                    return str(val)

                if self.filter_type_operation.currentText() == FilterTypeOperation.CONTAINS.value:
                    self.result_label.setText(f"Example: {', '.join([format_value(val) for val in unique_values[:3]])}")
                elif self.filter_type_operation.currentText() == FilterTypeOperation.EQUAL.value:
                    self.result_label.setText(f"Example: {format_value(unique_values[0])}")
                else:
                    self.result_label.setText(f"Example: {format_value(unique_values[0])}")

            except Exception as e:
                logging.error(f"Error getting a hint: {e}")
                self.result_label.setText("Error: \nCould not generate a hint.")

            return

        initial_population = self.df.shape[0]
        initial_indexes = list(self.df.index)
        self.filter_settings = FilterSettings(
            column_name=self.filter_column.currentText(),
            filter_type_remove_keep=FilterTypeRemoveKeep(self.filter_type_remove_keep.currentText()),
            filter_type_operation=FilterTypeOperation(self.filter_type_operation.currentText()),
            filter_value=self.filter_value.text(),
        )

        query = self.filter_settings.get_query()
        try:
            queried_df = self.df.query(query)
            final_population = queried_df.shape[0]
            final_indexes = list(queried_df.index)
            filtered_indexes = list(set(initial_indexes) - set(final_indexes))
            self.root_class.data_panel.tabledata.filtered_rows = filtered_indexes + self.already_filtered_rows
            self.root_class.data_panel.tabledata.data_changed()

            self.result_label.setText(
                f"Removing: {initial_population-final_population} respondents \n"
                f"Remaining: {final_population} respondents"
            )
            self.ok_button.setEnabled(True)
        except Exception as e:
            logging.debug(f"Filter error: {query}")
            logging.debug(e)
            self.root_class.data_panel.tabledata.filtered_rows = self.already_filtered_rows
            self.root_class.data_panel.tabledata.data_changed()
            self.result_label.setText(f"Invalid filter:\n{query}")
            self.ok_button.setEnabled(False)

    def clear(self):
        self.filter_type_remove_keep.setCurrentIndex(0)
        self.filter_column.setCurrentIndex(0)
        self.filter_type_operation.setCurrentIndex(0)
        self.filter_value.setText("")
        self.filter_changed()


class CompiledFilterHistory(BasePanelElement):
    def __init__(self, hover_highlight=True):
        super().__init__()
        self.hover_highlight = hover_highlight
        self.layout = None
        self.filter_widgets = []

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda widget, layout: [
                layout.setContentsMargins(4, 4, 4, 4),
                layout.setSpacing(0),
                set_stylesheet(
                    widget, "#id{border: 1px solid #aaa;}" "#id:hover{" "border: 1px solid rgb(0,120,215)" "}"
                )
                if self.hover_highlight
                else set_stylesheet(widget, "#id{border: 1px solid #aaa;}"),
            ],
        )

        self.label = widget_in_layout(
            widget=QLabelClickable(self.widget),
            layout=self.layout,
            setup=lambda widget, layout: [
                widget.setText("No Filters Applied"),
                set_stylesheet(widget, f"#id{{font-size: {Font.size_big}px; color: grey;}}"),
                widget.setAlignment(Qt.AlignmentFlag.AlignCenter),
                widget.clicked.connect(
                    lambda: self.handler(
                        Message(
                            message_type=MessageType.CLICKED,
                            payload=None,
                            caller_id=self.element_id,
                        )
                    )
                ),
            ],
        )

        self.widget_for_filters, self.layout_for_filters = empty_widget(
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QVBoxLayout,
            setup=lambda widget, layout: [
                layout.setContentsMargins(0, 0, 0, 0),
                layout.setSpacing(4),
            ],
        )

    def configure(self, filters: List[FilterSettings]):
        for filter_widget in self.filter_widgets:
            self.layout_for_filters.removeWidget(filter_widget)
            filter_widget.deleteLater()

        self.filter_widgets = []
        if len(filters) == 0:
            self.label.setText("No Active Filters")
        else:
            self.label.setText("Active Filters:")

        for i, filter_settings in enumerate(filters):
            filter_widget = widget_in_layout(
                widget=QLabelClickable(self.widget_for_filters),
                layout=self.layout_for_filters,
                setup=lambda widget, layout: [
                    widget.setText(filter_settings.get_text()),
                    widget.clicked.connect(
                        lambda _=i: self.handler(
                            Message(
                                message_type=MessageType.FILTER_CLICKED,
                                payload=_,
                                caller_id=self.element_id,
                            )
                        )
                    ),
                    widget.setWordWrap(True),
                    set_stylesheet(widget, f"#id{{border: 1px solid #ccc;}}"),
                ],
            )
            self.filter_widgets.append(filter_widget)
