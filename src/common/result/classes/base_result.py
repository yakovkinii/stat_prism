from typing import Dict

from src.common.result.classes.base_result_element import BaseResultElement
from src.common.result.classes.plot_result import PlotResultElement
from src.result_display_panel.result_widget_containers.plot_widget_container import (
    PlotResultElementWidgetContainerExport,
)


class BaseResult:
    def __init__(self, unique_id):
        # Unique integer id, not for display
        self.unique_id: int = unique_id
        # Result elements, each takes one tab
        self.result_elements: Dict[str, BaseResultElement] = {}
        # Display title (result selector)
        self.title: str = ...
        # Display title context (result display)
        self.title_context: str = ...
        # Settings panel index for activating the result
        self.settings_panel_index: int = ...
        # Result config
        self.config = ...
        # Flag for updating the result
        self.needs_update: bool = False

    def element_keys(self):
        return list(self.result_elements.keys())

    def configure(self, *args, **kwargs):
        pass

    def rename_column(self, old_name, new_name):
        pass

    def get_html(self):
        htmls = []
        for element in self.result_elements.values():
            if isinstance(element, PlotResultElement):
                htmls.append(element.get_html(renderer=PlotResultElementWidgetContainerExport))
            else:
                htmls.append(element.get_html())
        return "<br><br><br>".join(htmls)
