#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

from typing import Dict

from PySide6.QtWidgets import QVBoxLayout

from src.common.elements.base.base import BasePanelElement
from src.common.elements.utility.layout_helpers import empty_widget
from src.common.unique_qss import set_stylesheet


class Group(BasePanelElement):
    def __init__(self, elements: Dict[str, BasePanelElement]):
        super().__init__()
        self.elements = elements

    def inject(self, parent_widget, handler, element_id):
        self.element_id = element_id
        self.parent_widget = parent_widget
        self.handler = handler
        for sub_element_id, element in self.elements.items():
            element.inject(parent_widget, handler, sub_element_id)

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda widget, layout: [
                layout.setContentsMargins(3, 3, 3, 3),
                layout.setSpacing(2),
                set_stylesheet(widget, "#id{border: 1px solid #ddd;}"),
            ],
        )
        for element in self.elements.values():
            element.setup()
            self.layout.addWidget(element.widget)
