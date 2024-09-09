from typing import TYPE_CHECKING

from src.common.decorators import log_method, log_method_noarg
from src.common.elements.column_selector.column_selector import ColumnSelectorExPopup, ColumnSelectorPopupHolder
from src.common.elements.title.title import Title
from src.settings_panel.panels.base.base import BasePanel

if TYPE_CHECKING:
    pass


class ColumnSelector(BasePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(
                label_text="Select Columns",
            ),
            "popup_holder": ColumnSelectorPopupHolder(),
        }
        self.setup(stretch=True, navigation_elements=True, ok_button=True)

    @log_method
    def configure(self, popup: ColumnSelectorExPopup, caller_index, finished_handler):
        self.ok_button.setEnabled(False)
        self.caller_index = caller_index
        self.finished_handler = finished_handler
        self.popup = popup
        self.back_button.setEnabled(True)

        self.popup.on_moved_column_handler = self.column_moved

        self.elements["popup_holder"].configure(
            popup=popup,
        )

    @log_method_noarg
    def ok_button_pressed(self):
        self.popup.success = True
        self.activate_caller()
        self.finished_handler()

    @log_method_noarg
    def back_button_pressed(self):
        self.popup.success = False
        self.activate_caller()
        self.finished_handler()

    @log_method_noarg
    def column_moved(self):
        self.ok_button.setEnabled(True)
