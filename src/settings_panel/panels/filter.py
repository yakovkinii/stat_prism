import logging
from typing import TYPE_CHECKING, List

from src.common.custom_widget_containers import Title, FilterSetup, FilterSettings, CompiledFilterHistory, SpacerSmall
from src.common.decorators import log_method, log_method_noarg
from src.common.registry import DEBTS, DebtType, Debt
from src.data_panel.const import DataPanelState
from src.settings_panel.panels.base import BaseSettingsPanel

if TYPE_CHECKING:
    pass


class Filter(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(
            parent_widget, parent_class, root_class, stacked_widget_index, navigation_elements=True, ok_button=True
        )

        self.filters = []
        self.finished_handler = None
        self.result = None
        self.column_indexes = None
        self.caller_index = None
        self.max_plus_min = None
        self.elements = {
            "title": Title(
                parent_widget=self.widget_for_elements,
                label_text="Filter population",
            ),
            "compiled_filters":CompiledFilterHistory(
                parent_widget=self.widget_for_elements,
                filter_clicked_handler=self.compiled_filter_item_pressed,
            ),
            "spacer": SpacerSmall(parent_widget=self.widget_for_elements),
            "filter": FilterSetup(
                parent_widget=self.widget_for_elements,
                on_filter_added=self.on_filter_added,
            ),

        }

        self.place_elements()

    @log_method
    def configure(self, filters: List[FilterSettings], caller_index, finished_handler, selected_filter_index=None):
        self.ok_button.setEnabled(False)
        self.caller_index = caller_index
        self.finished_handler = finished_handler
        self.filters = filters
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
        dtypes = [self.tabledata.get_column_dtype(i) for i in range(number_of_columns)]


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
            dtypes=[self.tabledata.get_column_dtype(i) for i in range(len(self.tabledata.get_column_names()))],
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
            dtypes=[self.tabledata.get_column_dtype(i) for i in range(len(self.tabledata.get_column_names()))],
            filter_settings=clicked_filter,
            already_filtered_rows=removed_rows,
        )

