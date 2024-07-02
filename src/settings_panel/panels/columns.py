import logging
from typing import TYPE_CHECKING

from src.common.custom_widget_containers import Title, MediumAssButton, ColumnColorSelector
from src.settings_panel.panels.base import BaseSettingsPanel
from src.common.decorators import log_method, log_method_noarg

if TYPE_CHECKING:
    pass


class Columns(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(parent_widget, parent_class, root_class, stacked_widget_index)

        self.column_indexes = None
        self.caller_index = None
        self.elements = {
            "title2": Title(
                parent_widget=self.widget_for_elements,
                label_text="Properties",
            ),
            "color": ColumnColorSelector(
                parent_widget=self.widget_for_elements,
                handler=self.color_pressed,
            ),
            # "title": EditableTitleWordWrap(
            #     parent_widget=self.widget_for_elements,
            #     label_text="Title lorem ipsum trololo lorem ipsum trololo #1",
            #     handler=self.finish_editing_title,
            # ),
            "invert": MediumAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Invert\ncolumn ",
                icon_path="ri.arrow-up-down-line",
                # handler=self.inverse_handler,
            ),
            "add_col": MediumAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Add",
                icon_path="mdi.table-column-plus-after",
                handler=self.add_column_handler,
            ),
            "delete_col": MediumAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Delete columns",
                icon_path="mdi.table-column-remove",
                handler=self.delete_column_handler,
            ),
        }

        self.place_elements()

    @log_method
    def configure(self, column_indexes, caller_index=None):
        self.column_indexes = column_indexes
        self.caller_index = caller_index

        all_numeric = True
        for index in column_indexes:
            if self.tabledata.get_column_dtype(index) not in ["int"]:
                all_numeric = False
                break
        self.elements["invert"].widget.setEnabled(all_numeric)

    @log_method_noarg
    def inverse_handler(self):
        self.root_class.settings_panel.inverse_panel.configure(
            column_indexes=self.column_indexes, caller_index=self.stacked_widget_index
        )

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.inverse_panel_index)

    @log_method_noarg
    def add_column_handler(self):
        self.tabledata.add_column(max(self.column_indexes))
        self.root_class.action_select_table_column(max(self.column_indexes) + 1)
        self.root_class.action_activate_column_panel(max(self.column_indexes) + 1)

    @log_method_noarg
    def delete_column_handler(self):
        self.tabledata.delete_columns(self.column_indexes)

        new_index = min(self.column_indexes)

        if self.tabledata.columnCount() == 0:
            self.root_class.action_activate_home_panel()
            return
        if self.tabledata.columnCount() > new_index:
            self.root_class.action_select_table_column(new_index)
            self.root_class.action_activate_column_panel(new_index)
            return

        self.root_class.action_select_table_column(new_index - 1)
        self.root_class.action_activate_column_panel(new_index - 1)

    @log_method
    def color_pressed(self, color: int):
        logging.info(f"color {color} pressed")
        previous_colors = []
        for index in self.column_indexes:
            previous_colors.append(self.tabledata.get_column_color(index))

        if all([color == previous_color for previous_color in previous_colors]):
            color = None

        for index in self.column_indexes:
            self.tabledata.set_column_color(index, color)
