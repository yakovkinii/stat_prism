import logging
from typing import TYPE_CHECKING

from src.common.custom_widget_containers import BigAssButton, Title
from src.common.decorators import log_method_noarg
from src.core.correlation.correlation_result import CorrelationResult
from src.core.crosstab.crosstab_result import CrosstabResult
from src.core.descriptive.descriptive_result import DescriptiveResult
from src.core.filter.filter_result import FilterResult
from src.core.linearregr.linearregr_result import LinearregrResult
from src.settings_panel.panels.base import BaseSettingsPanel

if TYPE_CHECKING:
    pass


class SelectStudy(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        # Setup
        super().__init__(parent_widget, parent_class, root_class, stacked_widget_index)

        self.elements = {
            "title": Title(
                parent_widget=self.widget_for_elements,
                label_text="Add new study, how exciting! :)",
            ),
            "descriptive": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Descriptive",
                icon_path="fa.bar-chart",
                handler=self.add_descriptive,
            ),
            "correlations": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Correlations",
                icon_path="ph.chart-line-up-fill",
                handler=self.add_correlation,
            ),
            "filter": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Filter",
                icon_path="ph.chart-line-up-fill",
                handler=self.add_filter,
            ),

            "crosstab": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Crosstab",
                icon_path="ph.chart-line-up-fill",
                handler=self.add_crosstab,
            ),

            "linearregr": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Linearregr",
                icon_path="ph.chart-line-up-fill",
                handler=self.add_linearregr,
            ),
        }

        self.place_elements()

    @log_method_noarg
    def add_descriptive(self):
        result = DescriptiveResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.descriptive_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.descriptive_panel.configure(
            result=result, caller_index=self.stacked_widget_index
        )

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.descriptive_panel_index)

    @log_method_noarg
    def add_correlation(self):
        logging.info("add correlation clicked")
        result = CorrelationResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.correlation_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.correlation_panel.configure(
            result=result, caller_index=self.stacked_widget_index
        )

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.correlation_panel_index)

    @log_method_noarg
    def add_filter(self):
        logging.info("add filter clicked")
        result = FilterResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.filter_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.filter_panel.configure(result=result, caller_index=self.stacked_widget_index)

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.filter_panel_index)

    @log_method_noarg
    def add_crosstab(self):
        logging.info("add crosstab clicked")
        result = CrosstabResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.crosstab_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.crosstab_panel.configure(
            result=result, caller_index=self.stacked_widget_index
        )

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.crosstab_panel_index)

    @log_method_noarg
    def add_linearregr(self):
        logging.info("add linearregr clicked")
        result = LinearregrResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.linearregr_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.linearregr_panel.configure(
            result=result, caller_index=self.stacked_widget_index
        )

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.linearregr_panel_index)