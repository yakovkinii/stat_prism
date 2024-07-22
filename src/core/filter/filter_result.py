from typing import Union

from src.results_panel.results.common.base import BaseResult
from src.results_panel.results.common.html_element import HTMLResultElement


class FilterStudyConfig:
    def __init__(
        self,
    ):
        # result ID of the filter is always None (no nested filters)
        self.filter_id: Union[int, None] = None
        self.query: str = ""


class FilterResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, title=None, config: FilterStudyConfig = None):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id
        # Result elements, each takes one tab
        self.html = "html"
        self.result_elements = {self.html: HTMLResultElement()}
        # Display title (result selector)
        if title is None:
            title = f"Filter, id={unique_id}"
        self.title = title
        # Display title context (result display)
        self.title_context: str = ""
        # Settings panel index for activating the result
        self.settings_panel_index = settings_panel_index
        # Result config
        if config is None:
            self.config: FilterStudyConfig = FilterStudyConfig()
        else:
            self.config: FilterStudyConfig = config
        # Flag for updating the result
        self.needs_update: bool = False
