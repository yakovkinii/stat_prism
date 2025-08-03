#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import TYPE_CHECKING, List

from src._data_panel.const import DataPanelState
from src.common.debt import DEBTS, Debt, DebtType
from src.common.decorators import log_method, log_method_noarg
from src.common.elements.filter.filter import CompiledFilterHistory, FilterSettings, FilterSetup
from src.common.elements.spacer.spacer_small import SpacerSmall
from src.common.elements.title.title import Title
from src.common.messages import Message, MessageType
from src.settings_panel.panels.base.base import BasePanel

if TYPE_CHECKING:
    pass


class Filter(BasePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(
                label_text="Filter Population",
            ),
            "compiled_filters": CompiledFilterHistory(hover_highlight=False),
            "spacer": SpacerSmall(),
            "filter": FilterSetup(),
        }

        self.setup(stretch=True, navigation_elements=True, ok_button=True)

    @log_method
    def configure(self, filters: List[FilterSettings], caller_index, finished_handler, selected_filter_index=None):
        self.ok_button.setEnabled(False)
        self.caller_index = caller_index
        self.finished_handler = finished_handler
        self.filters = filters.copy()
        self.back_button.setEnabled(True)

        self.root_class.data_panel.tabledata.set_state(DataPanelState.FILTER)
        DEBTS.append(
            Debt(
                debt_type=[DebtType.ON_STUDY_CHANGE],
                resolve=lambda: self.root_class.data_panel.tabledata.set_state(DataPanelState.DEFAULT),
            )
        )

        all_column_names = self.tabledata.get_column_names()
        number_of_columns = len(all_column_names)
        dtypes = [self.tabledata.get_column_v2(i).column_dtype for i in range(number_of_columns)]

        df = self.tabledata.get_data()
        for filter_settings in filters:
            df = df.query(filter_settings.get_query())
        remaining_rows = list(df.index)
        removed_rows = [i for i in self.tabledata.get_data().index if i not in remaining_rows]

        self.elements["compiled_filters"].configure(self.filters)

        self.elements["filter"].configure(
            root_class=self.root_class,
            df=self.tabledata.get_data(),
            column_names=all_column_names,
            dtypes=dtypes,
            filter_settings=None,
            already_filtered_rows=removed_rows,
        )
        self.elements["filter"].filter_changed()

    @log_method
    def handler(self, message: Message):
        if message.message_type == MessageType.FILTER_ADDED:
            self.on_filter_added(message.payload)
        elif message.message_type == MessageType.FILTER_CLICKED:
            self.compiled_filter_item_pressed(message.payload)
        else:
            super().handler(message)

    @log_method
    def on_filter_added(self, filter_settings: FilterSettings):
        self.ok_button.setEnabled(True)
        self.filters.append(filter_settings)
        self.elements["compiled_filters"].configure(self.filters)

        df = self.tabledata.get_data()
        for filter_settings in self.filters:
            df = df.query(filter_settings.get_query())
        remaining_rows = list(df.index)
        removed_rows = [i for i in self.tabledata.get_data().index if i not in remaining_rows]

        self.elements["filter"].configure(
            root_class=self.root_class,
            df=self.tabledata.get_data(),
            column_names=self.tabledata.get_column_names(),
            dtypes=[
                self.tabledata.get_column_v2(i).column_dtype for i in range(len(self.tabledata.get_column_names()))
            ],
            filter_settings=None,
            already_filtered_rows=removed_rows,
        )

    @log_method_noarg
    def ok_button_pressed(self):
        self.finished_handler(self.filters)
        self.activate_caller()

    @log_method
    def compiled_filter_item_pressed(self, i):
        self.ok_button.setEnabled(True)
        clicked_filter = self.filters[i]
        self.filters.pop(i)

        self.elements["compiled_filters"].configure(self.filters)

        df = self.tabledata.get_data()
        for filter_settings in self.filters:
            df = df.query(filter_settings.get_query())
        remaining_rows = list(df.index)
        removed_rows = [i for i in self.tabledata.get_data().index if i not in remaining_rows]

        self.elements["filter"].configure(
            root_class=self.root_class,
            df=self.tabledata.get_data(),
            column_names=self.tabledata.get_column_names(),
            dtypes=[
                self.tabledata.get_column_v2(i).column_dtype for i in range(len(self.tabledata.get_column_names()))
            ],
            filter_settings=clicked_filter,
            already_filtered_rows=removed_rows,
        )
