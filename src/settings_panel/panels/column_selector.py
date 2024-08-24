from typing import TYPE_CHECKING

from src.common.custom_widget_containers import ColumnSelectorExPopup, ColumnSelectorPopupHolder, Title
from src.common.decorators import log_method, log_method_noarg
from src.settings_panel.panels.base import BaseSettingsPanel

if TYPE_CHECKING:
    pass


class ColumnSelector(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(
            parent_widget, parent_class, root_class, stacked_widget_index, navigation_elements=True, ok_button=True
        )

        self.finished_handler = None
        self.popup = None
        self.column_indexes = None
        self.caller_index = None
        self.max_plus_min = None
        self.elements = {
            "title": Title(
                parent_widget=self.widget_for_elements,
                label_text="Select columns",
            ),
            "popup_holder": ColumnSelectorPopupHolder(
                parent_widget=self.widget_for_elements,
            ),
        }
        self.place_elements()

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
