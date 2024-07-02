import logging
from typing import TYPE_CHECKING

from src.common.custom_widget_containers import ColumnColorSelector, EditableTitleWordWrap, MediumAssButton, Title
from src.common.decorators import log_method, log_method_noarg
from src.settings_panel.panels.base import BaseSettingsPanel

if TYPE_CHECKING:
    pass


class Column(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(parent_widget, parent_class, root_class, stacked_widget_index)

        self.column_index = None
        self.caller_index = None
        self.elements = {
            "title2": Title(
                parent_widget=self.widget_for_elements,
                label_text="Column properties",
            ),
            "title": EditableTitleWordWrap(
                parent_widget=self.widget_for_elements,
                label_text="Title lorem ipsum trololo lorem ipsum trololo #1",
                handler=self.finish_editing_title,
            ),
            "color": ColumnColorSelector(
                parent_widget=self.widget_for_elements,
                handler=self.color_pressed,
            ),
            "invert": MediumAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Invert\ncolumn ",
                icon_path="ri.arrow-up-down-line",
                handler=self.inverse_handler,
            ),
            "add_col": MediumAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Add",
                icon_path="mdi.table-column-plus-after",
                handler=self.add_column_handler,
            ),
            "delete_col": MediumAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Delete column",
                icon_path="mdi.table-column-remove",
                handler=self.delete_column_handler,
            ),
            "set_values": MediumAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Set values",
                icon_path="mdi.function",
                # handler=self.inverse_handler,
            ),
            # "debug": MediumAssButton(
            #     parent_widget=self.widget_for_elements,
            #     label_text="Debug",
            #     icon_path=None,
            #     handler=self.debug_handler,
            # ),
        }

        self.place_elements()

    @log_method
    def configure(self, column_index, caller_index=None):
        self.column_index = column_index
        self.caller_index = caller_index
        self.elements["title"].widget.setText(str(self.tabledata.get_column_name(self.column_index)))

        if self.tabledata.get_column_dtype(self.column_index) in ["int"]:
            self.elements["invert"].widget.setEnabled(True)
        else:
            self.elements["invert"].widget.setEnabled(False)
        # self.elements["title"].widget.setCursorPosition(0)

    @log_method_noarg
    def finish_editing_title(self):
        logging.info(
            f"column #{self.column_index} name changed from "
            f"{self.tabledata.get_column_name(self.column_index)} to "
            f"{self.elements['title'].widget.text()}"
        )
        if self.elements["title"].widget.text() not in self.tabledata.get_column_names():
            self.tabledata.rename_column(column_index=self.column_index, new_name=self.elements["title"].widget.text())
        else:
            logging.warning("Column name already exists, reverting")
            self.elements["title"].widget.setText(self.tabledata.get_column_name(self.column_index))
        self.root_class.action_select_table_column(self.column_index)

    @log_method_noarg
    def inverse_handler(self):
        self.root_class.settings_panel.inverse_panel.configure(
            column_indexes=[self.column_index], caller_index=self.stacked_widget_index
        )

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.inverse_panel_index)

    @log_method_noarg
    def add_column_handler(self):
        self.tabledata.add_column(self.column_index)
        self.root_class.action_select_table_column(self.column_index + 1)
        self.root_class.action_activate_column_panel(self.column_index + 1)

    @log_method_noarg
    def delete_column_handler(self):
        self.tabledata.delete_column(self.column_index)

        if self.tabledata.columnCount() == 0:
            self.root_class.action_activate_home_panel()
            return
        if self.tabledata.columnCount() > self.column_index:
            self.root_class.action_select_table_column(self.column_index)
            self.root_class.action_activate_column_panel(self.column_index)
            return

        self.root_class.action_select_table_column(self.column_index - 1)
        self.root_class.action_activate_column_panel(self.column_index - 1)

    @log_method
    def color_pressed(self, color: int):
        logging.info(f"color {color} pressed")
        previous_color = self.tabledata.get_column_color(self.column_index)
        if previous_color == color:
            color = None
        self.tabledata.set_column_color(self.column_index, color)
