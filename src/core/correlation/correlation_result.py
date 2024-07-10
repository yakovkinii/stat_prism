from typing import List

from src.results_panel.results.common.base import BaseResult
from src.results_panel.results.common.html_element import HTMLResultElement


class CorrelationStudyConfig:
    def __init__(
        self,
        selected_columns: List[str],
        compact: bool,
        report_only_significant: bool,
        # missing: bool,
        # mean: bool,
        # median: bool,
        # stddev: bool,
        # variance: bool,
        # minimum: bool,
        # maximum: bool,
    ):
        self.selected_columns = selected_columns
        self.compact = compact
        self.report_only_significant = report_only_significant
        # self.n = n
        # self.missing = missing
        # self.mean = mean
        # self.median = median
        # self.stddev = stddev
        # self.variance = variance
        # self.minimum = minimum
        # self.maximum = maximum


class CorrelationResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, title=None, config: CorrelationStudyConfig = None):
        super().__init__(unique_id)
        self.html = "html"
        self.result_elements = {self.html: HTMLResultElement()}
        self.settings_panel_index = settings_panel_index
        if title is None:
            title = "Correlation " + str(unique_id)
        self.title = title

        if config is None:
            self.config: CorrelationStudyConfig = CorrelationStudyConfig(
                selected_columns=[],
                compact=False,
                report_only_significant=True,
            )
        else:
            self.config: CorrelationStudyConfig = config
