from typing import List

from PySide6.QtWidgets import QVBoxLayout

from src.common.elements.base.base import BasePanelElement
from src.common.elements.utility.layout_helpers import empty_widget


class GroupExplicit(BasePanelElement):
    def __init__(self):
        super().__init__()
        self._elements: List[BasePanelElement] = []

    def setup(self):
        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda widget, layout: [
                layout.setContentsMargins(0, 0, 0, 0),
                layout.setSpacing(4),
            ],
        )

    def add_element(self, element: BasePanelElement):
        self._elements.append(element)
        self.layout.addWidget(element.widget)

    def get_elements(self, index: int) -> BasePanelElement:
        assert 0 <= index < len(self._elements), f"Index {index} out of bounds"
        return self._elements[index]

    def clear_elements(self):
        for element in self._elements:
            self.layout.removeWidget(element.widget)
            element.widget.deleteLater()

        self._elements = []
