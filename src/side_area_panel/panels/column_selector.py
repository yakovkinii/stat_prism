#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import TYPE_CHECKING

from src.common.decorators import log_method, log_method_noarg
from src.pyside_ext.elements.column_selector import (
    ColumnSelectorExPopup,
    ColumnSelectorPopupHolder,
)
from src.side_area_panel.panels.base import BasePanel

if TYPE_CHECKING:
    pass


class ColumnSelector(BasePanel):
    def setup_ui(self):
        self.elements = {
            "popup_holder": ColumnSelectorPopupHolder(),
        }
        self.setup(stretch=True, navigation_elements=True, ok_button=True, label="Select Columns")

    @log_method
    def configure(self, popup: ColumnSelectorExPopup, caller_index, finished_handler):
        # self._ok_button.setEnabled(False)
        self.caller_index = caller_index
        self.finished_handler = finished_handler
        self.popup = popup
        # self._back_button.setEnabled(True)

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
