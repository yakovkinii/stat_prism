from typing import List, Union

from src.common.custom_widget_containers import FilterSettings
from src.common.result.classes.base_result import BaseResult
from src.result_display_panel.result_widget_containers.html_widget_container import HTMLResultElement


class CorrelationStudyConfig:
    def __init__(
        self,
        selected_columns: List[str],
        compact: bool,
        report_only_significant: bool,
        filters: List[FilterSettings] = None,
    ):
        self.selected_columns = selected_columns
        self.compact = compact
        self.report_only_significant = report_only_significant
        self.filters: List[FilterSettings] = filters if filters is not None else []


class CorrelationResult(BaseResult):
    def __init__(
        self, unique_id, settings_panel_index, title=None, title_context=None, config: CorrelationStudyConfig = None
    ):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id
        # Result elements, each takes one tab
        self.html = "html"
        self.result_elements = {self.html: HTMLResultElement()}
        # Display title (result selector)
        if title is None:
            title = f"Correlation, id={unique_id}"
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
            self.config: CorrelationStudyConfig = CorrelationStudyConfig(
                selected_columns=[],
                compact=False,
                report_only_significant=True,
            )
        else:
            self.config: CorrelationStudyConfig = config
        # Flag for updating the result
        self.needs_update: bool = False
