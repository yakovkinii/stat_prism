import logging
from typing import TYPE_CHECKING

from src.common.column_flags import ColumnFlagsRegistry
from src.common.custom_widget_containers import Title, InvertVisualizer
from src.common.decorators import log_method, log_method_noarg
from src.settings_panel.panels.base import BaseSettingsPanel

if TYPE_CHECKING:
    pass


class Inverse(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(
            parent_widget, parent_class, root_class, stacked_widget_index, navigation_elements=True, ok_button=True
        )

        self.column_indexes = None
        self.caller_index = None
        self.max_plus_min = None
        self.elements = {
            "title": Title(
                parent_widget=self.widget_for_elements,
                label_text="Invert (flip) values",
            ),
            "invert_visualizer": InvertVisualizer(
                parent_widget=self.widget_for_elements,
            ),
            # "inverse": BigAssButton(
            #     parent_widget=self.widget_for_elements,
            #     label_text="Confirm",
            #     icon_path="mdi.dots-horizontal",
            #     handler=self.inverse_handler,
            # ),
        }

        self.place_elements()

    @log_method
    def configure(self, column_indexes, caller_index=None):
        self.column_indexes = column_indexes
        self.caller_index = caller_index
        if caller_index is not None:
            self.back_button.setEnabled(True)
        else:
            logging.warning("Unexpected absence of caller_index")
            self.back_button.setEnabled(False)

        columns = [self.tabledata.get_column(index) for index in column_indexes]
        unique_values = {value for column in columns for value in column.unique()}
        max_value = max([column.max() for column in columns])
        min_value = min([column.min() for column in columns])
        self.max_plus_min = max_value + min_value

        self.elements["invert_visualizer"].configure(
            unique_values=sorted(list(unique_values)),
            max_plus_min=self.max_plus_min,
        )

    @log_method_noarg
    def ok_button_pressed(self):
        for index in self.column_indexes:
            column = self.tabledata.get_column(index)
            column_name = self.tabledata.get_column_name(index)
            self.tabledata.set_column(
                index,
                self.max_plus_min-column,
            )
            self.tabledata.toggle_column_flag(
                column_name=column_name,
                flag=ColumnFlagsRegistry.inverted,
            )
        self.activate_caller()
