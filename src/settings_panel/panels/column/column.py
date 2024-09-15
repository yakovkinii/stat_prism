import logging
from typing import TYPE_CHECKING

from PySide6 import QtCore

from src.common.constant import ColumnType
from src.common.decorators import log_method, log_method_noarg
from src.common.elements.button.small_button import SmallButton
from src.common.elements.column_color_selector.column_color_selector import ColumnColorSelector
from src.common.elements.combo_box.combo_box import ComboBox
from src.common.elements.title.title import Title
from src.common.elements.title.title_editable import ColumnNameEditable
from src.common.messages import Message, MessageType
from src.settings_panel.panels.base.base import BasePanel
from src.settings_panel.panels.registry import PanelRegistry

if TYPE_CHECKING:
    pass


class Column(BasePanel):
    def setup_ui(self):
        self.elements = {
            "title2": Title(
                label_text="Column properties",
            ),
            "title": ColumnNameEditable(
                label_text="",
            ),
            "color": ColumnColorSelector(),
            "column_type": ComboBox(),
            "add_col": SmallButton(
                label_text="Add",
                icon_path="mdi.table-column-plus-after",
            ),
            "delete_col": SmallButton(
                label_text="Delete",
                icon_path="mdi.table-column-remove",
            ),
            "invert": SmallButton(
                label_text="Invert",
                icon_path="ri.arrow-up-down-line",
            ),
        }

        self.setup(stretch=True)

        self.configuring = True
        self.elements["column_type"].widget.addItems(
            [
                ColumnType.NOMINAL.value,
                ColumnType.ORDINAL.value,
                ColumnType.NUMERIC.value,
            ]
        )
        self.configuring = False

    @log_method
    def configure(self, column_index, caller_index=None):
        self.configuring = True
        self.column_index = column_index
        self.caller_index = caller_index
        self.elements["title"].widget.setText(str(self.tabledata.get_column_name(self.column_index)))

        self.elements["column_type"].widget.setCurrentText(self.tabledata.get_column_type(self.column_index).value)

        if self.tabledata.get_column_dtype(self.column_index) in ["int", "float"]:
            self.elements["invert"].widget.setEnabled(True)
        else:
            self.elements["invert"].widget.setEnabled(False)
        self.configuring = False

    @log_method_noarg
    def begin_edit_title(self):
        self.elements["title"].widget.setFocus()
        # select all after small delay

        # self.elements["title"].widget.selectAll()
        QtCore.QTimer.singleShot(100, self.elements["title"].widget.selectAll)

    @log_method
    def finish_editing_title(self, ok: bool):
        if not ok:
            logging.info("Title editing cancelled")
            self.configure(
                column_index=self.column_index,
                caller_index=self.caller_index,
            )
            return

        logging.debug(
            f"Trying changing column #{self.column_index} name changed from "
            f"{self.tabledata.get_column_name(self.column_index)} to "
            f"{self.elements['title'].widget.text()}"
        )

        title = self.elements["title"].widget.text()
        columns = self.tabledata.get_column_names()

        if title not in columns:
            self.tabledata.rename_column(column_index=self.column_index, new_name=title)
            self.root_class.action_select_table_column(self.column_index)
            return

        if title == columns[self.column_index]:
            logging.debug("Column name not changed")
            return
        # Modify column name

        suffix = 1
        while title + f" ({suffix})" in columns:
            suffix += 1
        title = title + f" ({suffix})"
        logging.info(f"Amended title to avoid conflict: {title}")
        self.tabledata.rename_column(column_index=self.column_index, new_name=title)
        self.root_class.action_select_table_column(self.column_index)
        self.configure(
            column_index=self.column_index,
            caller_index=self.caller_index,
        )

    @log_method_noarg
    def inverse_handler(self):
        PanelRegistry.INVERSE.ui_instance.configure(
            column_indexes=[self.column_index], caller_index=self.stacked_widget_index
        )

        self.root_class.action_activate_panel_by_index(PanelRegistry.INVERSE.settings_stacked_widget_index)

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

    @log_method
    def handler(self, message: Message):
        if self.configuring:
            return
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "invert":
                self.inverse_handler()
            elif message.caller_id == "add_col":
                self.add_column_handler()
            elif message.caller_id == "delete_col":
                self.delete_column_handler()
            elif message.caller_id == "color":
                self.color_pressed(message.payload)
            else:
                super().handler(message)
        elif message.message_type == MessageType.EDITING_FINISHED:
            if message.caller_id == "title":
                self.finish_editing_title(message.payload)
            else:
                super().handler(message)
        elif message.message_type == MessageType.STATE_CHANGED:
            if message.caller_id == "column_type":
                column_type = ColumnType(self.elements["column_type"].widget.currentText())
                self.tabledata.set_column_type(self.column_index, column_type)
                self.configure(
                    column_index=self.column_index,
                    caller_index=self.caller_index,
                )
        else:
            super().handler(message)
