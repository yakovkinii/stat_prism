#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

import logging
from typing import TYPE_CHECKING

from src.common.column_attributes import ColumnAttributesRegistry
from src.common.decorators import log_method, log_method_noarg
from src.common.elements.flip.flip import InvertVisualizer
from src.common.elements.title.title import Title
from src.settings_panel.panels.base.base import BasePanel

if TYPE_CHECKING:
    pass


class Inverse(BasePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(
                label_text="Invert (Flip) the Scale",
            ),
            "invert_visualizer": InvertVisualizer(),
        }

        self.setup(stretch=True, navigation_elements=True, ok_button=True)

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
                self.elements["invert_visualizer"].max_plus_min - column,
            )
            self.tabledata.toggle_column_flag(
                column_name=column_name,
                flag=ColumnAttributesRegistry.inverted,
            )
        self.activate_caller()
