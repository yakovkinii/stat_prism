import logging
from typing import TYPE_CHECKING

from PySide6 import QtWidgets

from src.common.result.registry import RESULTS
from src.common.unique_qss import set_stylesheet
from src.result_display_panel.result_widget_containers.registry import result_widget_container_registry

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class ResultDisplayClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        self.parent_widget = parent_widget

        self.widget = QtWidgets.QWidget(self.parent_widget)
        set_stylesheet(self.widget, "#id{background-color: #fff;}")
        self.widget.setContentsMargins(0, 0, 0, 0)
        self.layout = QtWidgets.QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.layout)

        self.element_widget_container = None
        self.element_id = None
        self.result_id = None

    def display_none(self):
        if self.element_widget_container is not None:
            self.layout.removeWidget(self.element_widget_container.widget)
            self.element_widget_container.widget.deleteLater()
        self.element_widget_container = None
        self.element_id = None
        self.result_id = None

    def display(self, result_id: int, element_id: str = None):
        logging.info(f"Displaying result {result_id} element {element_id}")
        if self.element_widget_container is not None:
            self.layout.removeWidget(self.element_widget_container.widget)
            self.element_widget_container.widget.deleteLater()

        self.result_id = result_id
        self.element_id = element_id

        result = RESULTS[result_id]
        if element_id is None:
            element_id = result.element_keys()[0]
        element = result.result_elements[element_id]

        self.element_widget_container = result_widget_container_registry[element.class_id](
            parent_widget=self.parent_widget, result_element=element
        )
        self.layout.addWidget(self.element_widget_container.widget)

    def refresh(self):
        self.display(self.result_id, self.element_id)


logging.debug("result display loaded")
