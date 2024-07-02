import logging
from typing import TYPE_CHECKING

from src.common.column_flags import ColumnFlagsRegistry
from src.common.custom_widget_containers import Title
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
        self.elements = {
            "title": Title(
                parent_widget=self.widget_for_elements,
                label_text="Invert (flip) values",
            ),
            # "title2": Title(
            #     parent_widget=self.widget_for_elements,
            #     label_text="",
            # ),
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

    @log_method_noarg
    def ok_button_pressed(self):
        column = self.tabledata.get_column(self.column_indexes)
        column_name = self.tabledata.get_column_name(self.column_indexes)
        self.tabledata.set_column(
            self.column_indexes,
            column.max() - (column - column.min()),
        )
        self.tabledata.toggle_column_flag(
            column_name=column_name,
            flag=ColumnFlagsRegistry.inverted,
        )
        self.activate_caller()
