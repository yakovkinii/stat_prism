#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import TYPE_CHECKING

from src.common.decorators import log_method, log_method_noarg
from src.common.elements.order.order import OrderVisualizer
from src.common.elements.title.title import Title
from src.settings_panel.panels.base.base import BasePanel

if TYPE_CHECKING:
    pass


class Order(BasePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(
                label_text="Confirm Order",
            ),
            "invert_visualizer": OrderVisualizer(),
        }
        self.setup(stretch=True, navigation_elements=True, ok_button=True)

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
