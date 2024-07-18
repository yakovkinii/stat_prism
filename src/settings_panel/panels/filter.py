from typing import TYPE_CHECKING

from src.common.custom_widget_containers import Title
from src.common.decorators import log_method
from src.core.filter.filter_result import FilterResult
from src.settings_panel.panels.base import BaseSettingsPanel

if TYPE_CHECKING:
    pass


class Filter(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(parent_widget, parent_class, root_class, stacked_widget_index)

        self.column_indexes = None
        self.caller_index = None
        self.max_plus_min = None
        self.elements = {
            "title": Title(
                parent_widget=self.widget_for_elements,
                label_text="Filter population",
            ),
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
        self.configuring = False
