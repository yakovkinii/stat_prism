import logging
from typing import TYPE_CHECKING, Union

from src.common.custom_widget_containers import BigAssCheckbox, ColumnSelector, SpacerSmall, Title
from src.common.decorators import log_method
from src.core.correlation.correlation_result import CorrelationResult, CorrelationStudyConfig
from src.core.correlation.main import recalculate_correlation_study
from src.settings_panel.panels.base import BaseSettingsPanel

if TYPE_CHECKING:
    pass


class Correlation(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(parent_widget, parent_class, root_class, stacked_widget_index, stretch=False, recalculate=True)

        self.study_index = None
        self.caller_index = None
        self.result: Union[CorrelationResult, None] = None
        self.elements = {
            "title2": Title(
                parent_widget=self.widget_for_elements,
                label_text="Correlation",
            ),
            "spacer": SpacerSmall(parent_widget=self.widget_for_elements),
            "compact": BigAssCheckbox(
                parent_widget=self.widget_for_elements,
                label_text="Compact table",
                handler=self.study_settings_changed,
            ),
            "report_only_significant": BigAssCheckbox(
                parent_widget=self.widget_for_elements,
                label_text="Report only significant correlations",
                handler=self.study_settings_changed,
            ),
            "spacer2": SpacerSmall(parent_widget=self.widget_for_elements),
            "column_selector": ColumnSelector(
                parent_widget=self.widget_for_elements,
            ),
        }
        self.elements["column_selector"].widget.selection_changed.connect(self.study_settings_changed)
        self.place_elements()

    @log_method
    def configure(self, result: CorrelationResult, caller_index=None):
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
        self.elements["compact"].widget.setChecked(config.compact)
        self.elements["report_only_significant"].widget.setChecked(config.report_only_significant)
        self.set_recalculate_button_highlight(result.needs_update)

        self.configuring = False

    def recalculate(self):
        if self.configuring:
            logging.error("Recalculate called while configuring.")
            return

        filter_result = None
        if self.result.config.filter_id is not None:
            filter_result = self.root_class.results_panel.results[self.result.config.filter_id]
        new_result = recalculate_correlation_study(
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
        config = CorrelationStudyConfig(
            selected_columns=selected_columns,
            compact=self.elements["compact"].widget.isChecked(),
            report_only_significant=self.elements["report_only_significant"].widget.isChecked(),
            filter_id=self.result.config.filter_id,
        )
        self.result.config = config
        self.result.needs_update = True
        self.set_recalculate_button_highlight(True)
        self.root_class.results_panel.result_selector.update_all()
