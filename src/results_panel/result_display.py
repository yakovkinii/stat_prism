import logging
from typing import TYPE_CHECKING

from PyQt5 import QtWidgets

from src.common.constant import DEBUG_LAYOUT
from src.common.unique_qss import set_stylesheet
from src.results_panel.results.common.base import BaseResult
from src.results_panel.results.registry import result_widget_container_registry

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class ResultDisplayClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        # tab widget
        self.widget = QtWidgets.QTabWidget()
        # self.widget.setContentsMargins(0, 0, 0, 0)
        self.widget.tabBar().setDocumentMode(True)
        self.widget.tabBar().setExpanding(False)
        self.element_widget_containers = []

        if DEBUG_LAYOUT:
            set_stylesheet(self.widget, "#id{border: 1px solid blue; background-color: #eef;}")

        # self.widget.addTab(QtWidgets.QLabel("Result1"), "Result1")
        # self.widget.addTab(QtWidgets.QLabel("Result2"), "Result2")
        # Increase the minimum size for tabs to prevent cutting off

        # Adjust the style of the tabs for better appearance

    def configure(self, result: BaseResult):
        self.widget.clear()
        self.element_widget_containers = []
        for element in result.result_elements.values():
            element_widget_container = result_widget_container_registry[element.class_id](self.widget, element)
            logging.debug("element_widget_container created")
            self.element_widget_containers.append(element_widget_container)  # To prevent garbage collection
            logging.debug("element_widget_container stored")
            try:
                logging.info("enter try")
                self.widget.addTab(element_widget_container.widget, element.title)
                logging.info("exit try")
            except Exception as e:
                logging.error(f"Error adding tab: {e}")
                raise ValueError()
            logging.debug("element_widget_container added to tab")
