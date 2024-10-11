from typing import List

from src.common.result.classes.base_result_element import BaseResultElement
from src.common.result.classes.html_result import HTMLResultElement, HTMLText
from src.common.result.classes.plot_result import PlotResultElement
from src.result_display_panel.result_widget_containers.plot_widget_container import (
    PlotResultElementWidgetContainerExport,
)
from src.settings_panel.panels.registry import PanelRegistry


class BaseResult:
    def __init__(self, unique_id):
        # Unique integer id, not for display
        self.unique_id: int = unique_id
        # Result elements, each takes one tab
        self.result_elements: List[BaseResultElement] = []
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

        self.description = ""

    @staticmethod
    def format_additional_info_html(text) -> str:
        return f"""
        <div style="color:#700; font-size:12pt"><b>{text}</b></div>
        <hr>
        """

    @staticmethod
    def format_description_html(text):
        return f"""
        <div style="color:#333">{text}</div>
        """

    def set_placeholder(
        self,
        additional_info_html: str = "Please configure the analysis using the panel on the right",
    ):
        self.result_elements = [
            HTMLResultElement(
                settings_panel_index=PanelRegistry.HTML_RESULT_ITEM_SETTINGS.settings_stacked_widget_index,
                items=[
                    HTMLText(
                        self.format_additional_info_html(additional_info_html)
                        + self.format_description_html(self.description)
                    )
                ],
                tab_title="Information",
            )
        ]

    def configure(self, *args, **kwargs):
        pass

    def rename_column(self, old_name, new_name):
        pass

    def get_html(self):
        htmls = []
        for element in self.result_elements:
            if isinstance(element, PlotResultElement):
                htmls.append(element.get_html(renderer=PlotResultElementWidgetContainerExport))
            else:
                htmls.append(element.get_html())
        return "<br>".join(htmls)
