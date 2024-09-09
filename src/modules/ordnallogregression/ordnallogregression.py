import logging
from typing import TYPE_CHECKING, Union

from src.common.decorators import log_method
from src.common.elements.custom_widget_containers import ColumnSelector, SpacerSmall, Title
from src.modules.base.base import BaseModulePanel
from src.modules.ordnallogregression.main import recalculate_ordnallogregression_study
from src.modules.ordnallogregression.ordnallogregression_result import (
    OrdnalLogRegressionResult,
    OrdnalLogRegressionStudyConfig,
)

if TYPE_CHECKING:
    pass


class OrdnalLogRegression(BaseModulePanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(
            parent_widget, parent_class, root_class, stacked_widget_index, stretch=False, study_elements=True
        )

        self.study_index = None
        self.caller_index = None
        self.result: Union[OrdnalLogRegressionResult, None] = None
        self.elements = {
            "title2": Title(
                parent_widget=self.widget_for_elements,
                label_text="OrdnalLogRegression",
            ),
            "spacer": SpacerSmall(parent_widget=self.widget_for_elements),
            "column_selector": ColumnSelector(
                parent_widget=self.widget_for_elements,
            ),
        }
        self.elements["column_selector"].widget.selection_changed.connect(self.study_settings_changed)
        self.place_elements()

    @log_method
    def configure(self, result: OrdnalLogRegressionResult, caller_index=None):
        self.configuring = True
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

        self.set_recalculate_button_highlight(result.needs_update)

        self.configuring = False

    def recalculate(self):
        if self.configuring:
            logging.error("Recalculate called while configuring.")
            return

        filter_result = None
        if self.result.config.filter_id is not None:
            filter_result = self.root_class.results_panel.results[self.result.config.filter_id]
        new_result = recalculate_ordnallogregression_study(
            df=self.tabledata.get_data(), result=self.result, filter_result=filter_result
        )
        new_result.needs_update = False
        self.result = new_result
        self.root_class.results_panel.update_result(new_result)
        self.set_recalculate_button_highlight(False)
        self.root_class.results_panel.result_selector.update_all()

    def study_settings_changed(self):
        if self.configuring:
            return

        selected_columns = self.elements["column_selector"].get_selected_columns()
        config = OrdnalLogRegressionStudyConfig(
            selected_columns=selected_columns,
            filter_id=self.result.config.filter_id,
        )
        self.result.config = config
        self.result.needs_update = True
        self.set_recalculate_button_highlight(True)
        self.root_class.results_panel.result_selector.update_all()
