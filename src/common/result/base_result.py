#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import List

from src.common.result.base_result_element import BaseResultElement
from src.common.result.html_result import HTMLTableV2
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style


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

        self.header = ""

    def init_header(self, title):
        self.header = HTML.div(HTML.bold(title), font_size=Style.FontSize.regular)

    def add_header_info(self, text):
        self.header += HTML.div(text, font_size=Style.FontSize.smaller)

    @staticmethod
    def format_additional_info_html(text) -> str:
        return HTML.div(HTML.bold(text), font_size=Style.FontSize.smaller)

    @staticmethod
    def format_description_html(text):
        return HTML.div(text)

    def set_placeholder(
        self,
        additional_info_html: str = "Please configure the analysis using the panel on the right",
    ):
        self.result_elements = [
            HTMLTableV2(
                texts=[
                    (
                        self.format_additional_info_html(additional_info_html)
                        + self.format_description_html(self.description)
                    )
                ]
            )
        ]

    def configure(self, *args, **kwargs):
        pass

    def rename_column(self, old_name, new_name):
        pass

    def get_html(self):
        htmls = [self.header]
        for element in self.result_elements:
            htmls.append(element.get_html())
        return "<br>".join(htmls)
