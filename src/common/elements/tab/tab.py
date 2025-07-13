#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#

from typing import Dict

from PySide6.QtWidgets import QTabWidget

from src.common.elements.base.base import BasePanelElement


class Tab(BasePanelElement):
    def __init__(self):
        super().__init__()
        self._elements: Dict[str, BasePanelElement] = {}

    def setup(self):
        self.widget = QTabWidget(self.parent_widget)
        self.widget.setTabPosition(QTabWidget.TabPosition.East)

    def add_element(self, name: str, element: BasePanelElement):
        self._elements[name] = element
        element.widget.show()
        self.widget.addTab(element.widget, name)

    def clear_elements(self):
        for key, element in self._elements.items():
            self.widget.removeTab(self.widget.indexOf(element.widget))
            element.widget.deleteLater()

        self._elements = {}

    def clear_elements_soft(self):
        for key, element in self._elements.items():
            self.widget.removeTab(self.widget.indexOf(element.widget))
            element.widget.hide()

        self._elements = {}
