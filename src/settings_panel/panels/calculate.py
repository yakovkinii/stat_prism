import logging
from typing import TYPE_CHECKING

from src.common.custom_widget_containers import ColumnSelector,  Title
from src.common.decorators import log_method, log_method_noarg
from src.settings_panel.panels.base import BaseSettingsPanel

if TYPE_CHECKING:
    pass


class Calculate(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(
            parent_widget,
            parent_class,
            root_class,
            stacked_widget_index,
            navigation_elements=True,
            ok_button=True,
            stretch=False,
        )

        self.column_index = None
        self.caller_index = None
        self.elements = {
            "title2": Title(
                parent_widget=self.widget_for_elements,
                label_text="Summate",
            ),
            "column_selector": ColumnSelector(
                parent_widget=self.widget_for_elements,
            ),
        }

        self.place_elements()

    @log_method
    def configure(self, column_index, caller_index=None):
        self.column_index = column_index
        self.caller_index = caller_index

        all_columns = self.tabledata.get_column_names()
        number_of_columns = len(all_columns)
        dtypes = [self.tabledata.get_column_dtype(i) for i in range(number_of_columns)]
        numeric_columns = [col for col, dtype in zip(all_columns, dtypes) if dtype in ["int", "float"]]
        self.elements["column_selector"].configure(
            columns=all_columns, selected_columns=[], allowed_columns=numeric_columns
        )

    @log_method_noarg
    def ok_button_pressed(self):
        selected_columns = self.elements["column_selector"].get_selected_columns()
        if len(selected_columns) == 0:
            logging.debug("No columns selected")
            return

        result = self.tabledata.get_columns(selected_columns).sum(axis=1)
        self.tabledata.set_column(self.column_index, result)
        self.activate_caller()
