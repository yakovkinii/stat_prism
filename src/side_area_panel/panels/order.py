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


from typing import TYPE_CHECKING

from src.common.decorators import log_method, log_method_noarg
from src.pyside_ext.elements.order import OrderVisualizer
from src.side_area_panel.panels.base import BasePanel

if TYPE_CHECKING:
    pass


class Order(BasePanel):
    def setup_ui(self):
        self.elements = {
            "invert_visualizer": OrderVisualizer(),
        }
        self.setup(stretch=True, navigation_elements=True, ok_button=True, label="Configure Order")

    @log_method
    def configure(self, column_index, caller_index=None):
        self.column_index = column_index
        self.caller_index = caller_index
        self.back_button.setEnabled(True)

        ordinal_order = self.tabledata.get_column_ordinal_order(column_index)
        keys_sorted_by_values = sorted(ordinal_order, key=ordinal_order.get)
        self.elements["invert_visualizer"].configure(
            values=keys_sorted_by_values,
        )

    @log_method_noarg
    def ok_button_pressed(self):
        order_dict = self.elements["invert_visualizer"].get_order_dict()
        self.tabledata.set_column_ordinal_order(self.column_index, order_dict)
        self.activate_caller()
