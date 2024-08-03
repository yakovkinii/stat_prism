import logging
from typing import TYPE_CHECKING

from src.common.custom_widget_containers import BigAssButton, Title
from src.common.decorators import log_method_noarg
from src.core.anova.anova_result import AnovaResult
from src.core.binomiallogregression.binomiallogregression_result import BinomialLogRegressionResult
from src.core.correlation.correlation_result import CorrelationResult
from src.core.crosstab.crosstab_result import CrosstabResult
from src.core.descriptive.descriptive_result import DescriptiveResult
from src.core.efa.efa_result import EFAResult
from src.core.filter.filter_result import FilterResult
from src.core.kruskalwallis.kruskalwallis_result import KruskalWallisResult
from src.core.linearregr.linearregr_result import LinearregrResult
from src.core.multinomiallogregression.multinomiallogregression_result import MultinomialLogRegressionResult
from src.core.ordnallogregression.ordnallogregression_result import OrdnalLogRegressionResult
from src.core.partcorrelation.partcorrelation_result import PartCorrelationResult
from src.core.reliability.reliability_result import ReliabilityResult
from src.core.ttest.ttest_result import TTestResult
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
            "kruskalwallis": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Pruskalwallis",
                icon_path="ph.chart-line-up-fill",
                handler=self.add_kruskalwallis,
            ),
            "partcorrelation": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Partcorrelation",
                icon_path="ph.chart-line-up-fill",
                handler=self.add_partcorrelation,
            ),
            "binomiallogregression": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Binomiallogregression",
                icon_path="ph.chart-line-up-fill",
                handler=self.add_binomiallogregression,
            ),
            "multinomiallogregression": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Multinomiallogregression",
                icon_path="ph.chart-line-up-fill",
                handler=self.add_multinomiallogregression,
            ),
            "ordnallogregression": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Ordnallogregression",
                icon_path="ph.chart-line-up-fill",
                handler=self.add_ordnallogregression,
            ),
            "reliability": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Reliability",
                icon_path="ph.chart-line-up-fill",
                handler=self.add_reliability,
            ),
            "efa": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="EFA",
                icon_path="ph.chart-line-up-fill",
                handler=self.add_efa,
            ),
            "ttest": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="TTest",
                icon_path="ph.chart-line-up-fill",
                handler=self.add_ttest,
            ),
            "anova": BigAssButton(
                parent_widget=self.widget_for_elements,
                label_text="Anova",
                icon_path="ph.chart-line-up-fill",
                handler=self.add_anova,
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

        self.root_class.settings_panel.crosstab_panel.configure(result=result, caller_index=self.stacked_widget_index)

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.crosstab_panel_index)

    @log_method_noarg
    def add_linearregr(self):
        logging.info("add linearregr clicked")
        result = LinearregrResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.linearregr_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.linearregr_panel.configure(result=result, caller_index=self.stacked_widget_index)

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.linearregr_panel_index)

    @log_method_noarg
    def add_kruskalwallis(self):
        logging.info("add kruskalwallis clicked")
        result = KruskalWallisResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.kruskalwallis_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.kruskalwallis_panel.configure(
            result=result, caller_index=self.stacked_widget_index
        )

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.kruskalwallis_panel_index)

    @log_method_noarg
    def add_partcorrelation(self):
        logging.info("add partcorrelation clicked")
        result = PartCorrelationResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.partcorrelation_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.partcorrelation_panel.configure(
            result=result, caller_index=self.stacked_widget_index
        )

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.partcorrelation_panel_index)

    @log_method_noarg
    def add_binomiallogregression(self):
        logging.info("add binomiallogregression clicked")
        result = BinomialLogRegressionResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.binomiallogregression_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.binomiallogregression_panel.configure(
            result=result, caller_index=self.stacked_widget_index
        )

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.binomiallogregression_panel_index)

    @log_method_noarg
    def add_multinomiallogregression(self):
        logging.info("add multinomiallogregression clicked")
        result = MultinomialLogRegressionResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.multinomiallogregression_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.multinomiallogregression_panel.configure(
            result=result, caller_index=self.stacked_widget_index
        )

        self.root_class.action_activate_panel_by_index(
            self.root_class.settings_panel.multinomiallogregression_panel_index
        )

    @log_method_noarg
    def add_ordnallogregression(self):
        logging.info("add ordnallogregression clicked")
        result = OrdnalLogRegressionResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.ordnallogregression_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.ordnallogregression_panel.configure(
            result=result, caller_index=self.stacked_widget_index
        )

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.ordnallogregression_panel_index)

    @log_method_noarg
    def add_reliability(self):
        logging.info("add reliability clicked")
        result = ReliabilityResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.reliability_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.reliability_panel.configure(
            result=result, caller_index=self.stacked_widget_index
        )

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.reliability_panel_index)

    @log_method_noarg
    def add_efa(self):
        logging.info("add efa clicked")
        result = EFAResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.efa_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.efa_panel.configure(result=result, caller_index=self.stacked_widget_index)

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.efa_panel_index)

    @log_method_noarg
    def add_ttest(self):
        logging.info("add ttest clicked")
        result = TTestResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.ttest_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.ttest_panel.configure(result=result, caller_index=self.stacked_widget_index)

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.ttest_panel_index)

    @log_method_noarg
    def add_anova(self):
        logging.info("add anova clicked")
        result = AnovaResult(
            unique_id=self.root_class.results_panel.get_unique_id(),
            settings_panel_index=self.root_class.settings_panel.anova_panel_index,
        )
        self.root_class.results_panel.add_result(result)

        self.root_class.settings_panel.anova_panel.configure(result=result, caller_index=self.stacked_widget_index)

        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.anova_panel_index)
