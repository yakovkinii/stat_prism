from typing import List, Union

from src.results_panel.results.common.base import BaseResult
from src.results_panel.results.common.html_element import HTMLResultElement


class EFAStudyConfig:
    def __init__(
        self,
        selected_columns: List[str],
        filter_id: Union[int, None] = None,
    ):
        self.selected_columns = selected_columns

        # result ID of the filter or None
        self.filter_id: Union[int, None] = filter_id


class EFAResult(BaseResult):
    def __init__(
        self, unique_id, settings_panel_index, title=None, title_context=None, config: EFAStudyConfig = None
    ):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id
        # Result elements, each takes one tab
        self.html = "html"
        self.result_elements = {self.html: HTMLResultElement()}
        # Display title (result selector)
        if title is None:
            title = f"EFA, id={unique_id}"
        self.title = title
        # Display title context (result display)
        if title_context is None:
            if config is None:
                title_context = ""
            else:
                title_context = ", ".join([f"{col[:8]}" if len(col) > 8 else col for col in config.selected_columns])
        self.title_context = title_context
        # Settings panel index for activating the result
        self.settings_panel_index = settings_panel_index
        # Result config
        if config is None:
            self.config: EFAStudyConfig = EFAStudyConfig(
                selected_columns=[],

            )
        else:
            self.config: EFAStudyConfig = config
        # Flag for updating the result
        self.needs_update: bool = False
