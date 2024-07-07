import logging
from typing import TYPE_CHECKING

from src.common.custom_widget_containers import ColumnSelector, EditableTitleWordWrap, MediumAssButton, Title
from src.common.decorators import log_method, log_method_noarg
from src.core.descriptive.core import recalculate_descriptive_study
from src.core.descriptive.objects import DescriptiveStudyConfig
from src.results_panel.results.descriptive_result import DescriptiveResult
from src.settings_panel.panels.base import BaseSettingsPanel

if TYPE_CHECKING:
    pass


class Descriptive(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(parent_widget, parent_class, root_class, stacked_widget_index, stretch=False)

        self.study_index = None
        self.caller_index = None
        self.result = None
        self.elements = {
            "title2": Title(
                parent_widget=self.widget_for_elements,
                label_text="Descriptive",
            ),
            # "edit": EditableTitleWordWrap(
            #     parent_widget=self.widget_for_elements,
            #     label_text="",
            #     handler=self.finish_editing,
            # ),
            "column_selector": ColumnSelector(
                parent_widget=self.widget_for_elements,
            ),
        }
        self.elements["column_selector"].widget.selection_changed.connect(self.selection_changed)
        self.place_elements()

    @log_method
    def configure(self, result: DescriptiveResult, caller_index=None):
        self.caller_index = caller_index
        self.result = result

        all_columns = self.tabledata.get_column_names()
        number_of_columns = len(all_columns)
        dtypes = [self.tabledata.get_column_dtype(i) for i in range(number_of_columns)]
        numeric_columns = [col for col, dtype in zip(all_columns, dtypes) if dtype in ["int", "float"]]

        config = result.config

        self.elements["column_selector"].configure(
            columns=all_columns, selected_columns=config.selected_columns, allowed_columns=numeric_columns
        )

    @log_method_noarg
    def ok_button_pressed(self):
        # selected_columns = self.elements["column_selector"].get_selected_columns()
        # if len(selected_columns) == 0:
        #     logging.debug("No columns selected")
        #     return
        #
        # result = self.tabledata.get_columns(selected_columns).sum(axis=1)
        # self.tabledata.set_column(self.column_index, result)
        # self.activate_caller()
        ...

    def selection_changed(self):
        selected_columns = self.elements["column_selector"].get_selected_columns()
        config = DescriptiveStudyConfig(
            selected_columns=selected_columns,
        )
        self.result.config = config
        new_result = recalculate_descriptive_study(df=self.tabledata.get_data(), result=self.result)
        self.root_class.results_panel.update_result(new_result)
