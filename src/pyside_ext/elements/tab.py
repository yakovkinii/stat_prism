#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import Dict

from PySide6.QtWidgets import QTabWidget, QWidget

from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.layout import VBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style


class Tab(BasePanelElement):
    def __init__(self):
        super().__init__()
        self._element_widgets: Dict[str, QWidget] = {}

    def setup(self):
        self.widget = QTabWidget(self.parent_widget)
        self.widget.setTabPosition(QTabWidget.TabPosition.East)
        self.widget.tabBar().setDocumentMode(True)
        self.widget.tabBar().setExpanding(False)

    def add_element(self, name: str, element: BasePanelElement):
        widget, layout = add_widget(
            inner_layout_class=VBoxLayout,
            css=css(background_color=Style.Color.BackgroundElevated, border=Style.General.border_elevated),
        )
        layout.addWidget(element.widget)

        element.widget.show()
        self._element_widgets[name] = widget
        self.widget.addTab(widget, name)

    def clear_elements(self):
        for key, widget in self._element_widgets.items():
            self.widget.removeTab(self.widget.indexOf(widget))
            widget.deleteLater()

        self._element_widgets = {}

    def clear_elements_soft(self):
        for key, widget in self._element_widgets.items():
            self.widget.removeTab(self.widget.indexOf(widget))
            widget.hide()

        self._element_widgets = {}
