import logging
from typing import TYPE_CHECKING

from src.common.custom_widget_containers import ColumnFilter, Title
from src.common.decorators import log_method, log_method_noarg
from src.core.filter.filter_result import FilterResult
from src.settings_panel.panels.base import BaseSettingsPanel

if TYPE_CHECKING:
    pass


class Filter(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(parent_widget, parent_class, root_class, stacked_widget_index)

        self.result = None
        self.column_indexes = None
        self.caller_index = None
        self.max_plus_min = None
        self.elements = {
            "title": Title(
                parent_widget=self.widget_for_elements,
                label_text="Filter population",
            ),
            "filter": ColumnFilter(parent_widget=self.widget_for_elements, on_change_handler=self.filter_changed),
            # "inverse": BigAssButton(
            #     parent_widget=self.widget_for_elements,
            #     label_text="Confirm",
            #     icon_path="mdi.dots-horizontal",
            #     handler=self.inverse_handler,
            # ),
        }

        self.place_elements()

    @log_method
    def configure(self, result: FilterResult, caller_index=None):
        self.configuring = True
        self.caller_index = caller_index
        self.result = result
        self.elements["filter"].filter_value.setText(result.config.query)
        self.configuring = False

    @log_method_noarg
    def filter_changed(self):
        query = self.elements["filter"].filter_value.text()
        try:
            df = self.root_class.data_panel.tabledata.get_data()
            queried_df = df.query(query)
            if queried_df.empty:
                raise Exception("Query returned no results.")
            logging.info(f"Query returned {queried_df.shape[0]} rows.")
        except Exception as e:
            logging.error(e)
            return

        self.result.config.query = query
