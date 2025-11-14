#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from abc import abstractmethod
from typing import List

from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QWidget

from src.common.decorators import log_method_noarg
from src.common.messages import Message, MessageType
from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.elements.utility.layout_helpers import add_widget, empty_widget
from src.pyside_ext.layout import HBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACSpacer(ItemInSidePanelWithAutoConfig):
    def post_init(self, name, parent_widget):
        self.name = name

        self.widget = QWidget(parent_widget)
        self.widget.setFixedHeight(20)

    def get_kwargs(self):
        return {}

    def configure(self, **kwargs):
        pass

    @log_method_noarg
    def set_alert(self):
        pass

    @log_method_noarg
    def clear_alert(self):
        pass
