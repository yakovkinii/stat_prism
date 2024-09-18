from enum import Enum
from typing import Dict, List

from src.common.elements.filter.filter import FilterSettings
from src.common.result.classes.base_result import BaseResult
from src.common.result.classes.plot_result import PlotResultElement
from src.result_display_panel.result_widget_containers.html_widget_container import HTMLResultElement
from src.settings_panel.panels.registry import PanelRegistry


class CorrelationType(Enum):
    PEARSON = 0
    SPEARMAN = 1
    KENDALL = 2


CORRELATION_TYPE_MAP = {
    "Pearson": CorrelationType.PEARSON,
    "Spearman": CorrelationType.SPEARMAN,
    "Kendall": CorrelationType.KENDALL,
}


class CorrelationStudyConfig:
    def __init__(
        self,
        selected_columns: List[str] = None,
        correlation_type: CorrelationType = CorrelationType.PEARSON,
        compact: bool = False,
        generate_plots: bool = False,
        report_only_significant: bool = True,
        filters: List[FilterSettings] = None,
    ):
        self.selected_columns = selected_columns if selected_columns is not None else []
        self.compact = compact
        self.generate_plots = generate_plots
        self.correlation_type = correlation_type
        self.report_only_significant = report_only_significant
        self.filters: List[FilterSettings] = filters if filters is not None else []


class CorrelationResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, title, title_context, config: CorrelationStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id
        # Result elements, each takes one tab

        self.html_element: HTMLResultElement = HTMLResultElement(
            settings_panel_index=PanelRegistry.HTML_RESULT_ITEM_SETTINGS.settings_stacked_widget_index
        )
        self.plot_elements: Dict[str, PlotResultElement] = {}
        self.result_elements = {"html_element": self.html_element}

        self.title = title
        # Display title context (result display)
        # if title_context is None:
        #     if config is None:
        #         title_context = ""
        #     else:
        #         title_context = ", ".join([f"{col[:8]}" if len(col) > 8 else col for col in config.selected_columns])
        self.title_context = title_context
        # Settings panel index for activating the result
        self.settings_panel_index = settings_panel_index
        # Result config
        # if config is None:
        #     self.config: CorrelationStudyConfig = CorrelationStudyConfig(
        #         selected_columns=[],
        #         compact=False,
        #         report_only_significant=True,
        #     )
        # else:
        self.config: CorrelationStudyConfig = config
        # Flag for updating the result
        self.needs_update: bool = False

    def set_elements(self, html_element: HTMLResultElement, plot_elements: Dict[str, PlotResultElement]):
        self.html_element = html_element
        self.plot_elements = plot_elements
        self.result_elements = {"html_element": self.html_element}
        for key, value in self.plot_elements.items():
            self.result_elements[key] = value

    def rename_column(self, old_name, new_name):
        self.config.selected_columns = [new_name if col == old_name else col for col in self.config.selected_columns]
        self.needs_update = True
