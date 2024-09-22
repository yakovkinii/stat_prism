from typing import Dict, List

from src.common.elements.filter.filter import FilterSettings
from src.common.result.classes.base_result import BaseResult
from src.common.result.classes.html_result import HTMLText
from src.common.result.classes.plot_result import PlotResultElement
from src.result_display_panel.result_widget_containers.html_widget_container import HTMLResultElement
from src.settings_panel.panels.registry import PanelRegistry

DESCRIPTION = """
<h1> Descriptive Statistics </h1>
<h3> Description </h3>
<div>
    Descriptive statistics summarize the main features of a dataset.
</div>
"""


class DescriptiveStudyConfig:
    def __init__(
        self,
        selected_columns1: List[str] = None,
        selected_columns2: List[str] = None,
        filters: List[FilterSettings] = None,
    ):
        self.selected_columns1 = selected_columns1 if selected_columns1 is not None else []
        self.selected_columns2 = selected_columns2 if selected_columns2 is not None else []
        self.filters: List[FilterSettings] = filters if filters is not None else []


class DescriptiveResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, title, title_context, config: DescriptiveStudyConfig):
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

        self.title_context = title_context
        self.settings_panel_index = settings_panel_index
        self.config: DescriptiveStudyConfig = config

        self.needs_update: bool = False
        self.set_placeholder()

    def set_placeholder(self, additional_info_html: str = ""):
        self.html_element.items = [HTMLText(additional_info_html + DESCRIPTION)]
        self.plot_elements: Dict[str, PlotResultElement] = {}
        self.result_elements = {"html_element": self.html_element}

    def set_elements(self, html_element: HTMLResultElement, plot_elements: Dict[str, PlotResultElement]):
        self.html_element = html_element
        self.plot_elements = plot_elements
        self.result_elements = {"html_element": self.html_element}
        for key, value in self.plot_elements.items():
            self.result_elements[key] = value

    def rename_column(self, old_name, new_name):
        self.config.selected_columns1 = [new_name if col == old_name else col for col in self.config.selected_columns1]
        self.config.selected_columns2 = [new_name if col == old_name else col for col in self.config.selected_columns2]
        self.needs_update = True
