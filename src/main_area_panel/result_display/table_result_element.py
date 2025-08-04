#  Copyright (c) 2023 StatPrism Team. All rights reserved.


#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from PySide6.QtWidgets import QVBoxLayout

from src.common.constant import BASE_STYLES
from src.common.decorators import log_method
from src.common.elements.utility.layout_helpers import empty_widget, widget_in_layout
from src.common.elements.utility.primitive_elements import QWidgetClickable
from src.common.result.registry import RESULTS
from src.main_area_panel.result_display.base import BaseResultDisplay
from src.main_area_panel.result_display.elements.result_element_label import ResultElementLabel
from src.main_area_panel.result_display.elements.text_browser import TextBrowser
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class TableResultElementDisplay(BaseResultDisplay):
    def __init__(self, parent_widget, parent_class, root_class, label_text: str, result_id, result_element_id):
        super().__init__(parent_widget, parent_class, root_class)
        self.result_id = result_id
        self.result_element_id = result_element_id

        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
        )
        set_stylesheet(self.widget, css(background_color=Style.Color.Background))

        self.header_widget, self.header_layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [w.clicked.connect(lambda: self.activate_result(self.result_id, self.result_element_id))],
        )

        self.label = widget_in_layout(
            widget=ResultElementLabel(parent=self.header_widget, label_text=label_text),
            layout=self.header_layout,
            setup=lambda w, l: [
                w.clicked.connect(
                    lambda: self.activate_result(self.result_id, self.result_element_id)
                )
            ],
        )

        self.text_browser = widget_in_layout(
            widget=TextBrowser(self.widget),
            layout=self.layout,
        )
        self.refresh()

    def refresh(self):
        self.text_browser.set_html(
            BASE_STYLES + RESULTS[self.result_id].result_elements[self.result_element_id].get_html()
        )

    @log_method
    def activate_result(self, result_id, result_element_id):
        self.parent_class.activate_result(result_id, result_element_id)
