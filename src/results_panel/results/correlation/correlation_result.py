from typing import List

from src.results_panel.results.common.base import BaseResult
from src.results_panel.results.correlation.correlation_table_element import CorrelationTableResultElement
from src.results_panel.results.descriptive.descriptive_table_element import DescriptiveTableResultElement
from src.results_panel.results.common.text_element import TextResultElement


class CorrelationStudyConfig:
    def __init__(
        self,
        selected_columns: List[str],
        # n: bool,
        # missing: bool,
        # mean: bool,
        # median: bool,
        # stddev: bool,
        # variance: bool,
        # minimum: bool,
        # maximum: bool,
    ):
        self.selected_columns = selected_columns
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
        self.table = "table"
        self.description = "description"
        self.result_elements = {
            self.table: CorrelationTableResultElement(
                html="",
            ),
            self.description: TextResultElement(text=""),
        }
        self.settings_panel_index = settings_panel_index
        if title is None:
            title = "Correlation "+str(unique_id)
        self.title = title

        if config is None:
            self.config: CorrelationStudyConfig = CorrelationStudyConfig(
                selected_columns=[],
            )
        else:
            self.config: CorrelationStudyConfig = config