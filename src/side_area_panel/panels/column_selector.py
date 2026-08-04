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


from src.common.decorators import log_method, log_method_noarg
from src.pyside_ext.elements.column_selector import ColumnSelectorExPopup, ColumnSelectorPopupHolder
from src.side_area_panel.panels.base import BasePanel


class ColumnSelector(BasePanel):
    def setup_ui(self):
        self.elements = {
            "popup_holder": ColumnSelectorPopupHolder(),
        }
        self.setup(stretch=True, navigation_elements=True, ok_button=True, label="Select Columns")

    @log_method
    def configure(self, popup: ColumnSelectorExPopup, caller_index, finished_handler):
        self.caller_index = caller_index
        self.finished_handler = finished_handler
        self.popup = popup

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
