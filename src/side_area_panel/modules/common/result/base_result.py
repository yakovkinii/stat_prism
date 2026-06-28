#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import List, Dict

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.base_result_element import (
    BaseResultElement,
)
from src.side_area_panel.modules.common.result.html_result import HTMLTableV2


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
        # For keeping the user settings
        self.old_result_elements: Dict[str, BaseResultElement] = dict()

        self.description = ""
        # Validation / status message for data-processing cards. Shown (red) in the card's
        # short summary when a step can't compute (e.g. no column selected); "" when fine.
        self.error_message = ""

        self.header = ""

    def init_header(self, title):
        self.header = HTML.div(HTML.bold(title), font_size=Style.FontSize.regular)

    def add_header_info(self, text):
        self.header += HTML.div(text, font_size=Style.FontSize.smaller)

    def update_and_add_element(self, element:BaseResultElement, name: str):
        if name in self.old_result_elements:
            element.load_settings_from(self.old_result_elements[name])
        self.result_elements.append(element)
        self.old_result_elements[name] = element

    @staticmethod
    def format_additional_info_html(text) -> str:
        return HTML.div(HTML.bold(text), font_size=Style.FontSize.smaller) + HTML.hr()

    @staticmethod
    def format_description_html(text):
        return HTML.div(text)

    def set_placeholder(self, additional_info_html: str = None):
        # Only the short hint is shown on the empty screen; the full description &
        # methodology fine-print live behind the info (i) button so they don't clutter
        # the default view.
        if additional_info_html is None:
            additional_info_html = t("common.configure_hint")
        self.result_elements = [
            HTMLTableV2(
                texts=[HTML.div(HTML.bold(additional_info_html), font_size=Style.FontSize.smaller)]
            )
        ]

    def set_error(self, message: str):
        """Show only the error / validation message (muted dark red). The description &
        methodology stay behind the info (i) button, same as the configure placeholder."""
        error_html = HTML.div(
            HTML.bold(message),
            color=Style.Color.Danger.value,
            font_size=Style.FontSize.smaller,
        )
        self.result_elements = [HTMLTableV2(texts=[error_html])]

    def configure(self, *args, **kwargs):
        pass

    def update_description(self):
        pass

    def rename_column(self, old_name, new_name):
        pass

    def get_html(self):
        htmls = [self.header]
        for element in self.result_elements:
            htmls.append(element.get_html())
        return "<br>".join(htmls)
