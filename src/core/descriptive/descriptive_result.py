from typing import List

from src.results_panel.results.common.base import BaseResult

from src.results_panel.results.common.html_element import HTMLResultElement


class DescriptiveStudyConfig:
    def __init__(
        self,
        selected_columns: List[str],
    ):
        self.selected_columns = selected_columns



class DescriptiveResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, title=None, config: DescriptiveStudyConfig = None):
        super().__init__(unique_id)
        self.html = "html"
        self.result_elements = {
            self.html: HTMLResultElement(
            ),
        }
        self.settings_panel_index = settings_panel_index
        if title is None:
            title = "Descriptive "+str(unique_id)
        self.title = title

        if config is None:
            self.config: DescriptiveStudyConfig = DescriptiveStudyConfig(
                selected_columns=[],
            )
        else:
            self.config: DescriptiveStudyConfig = config
