#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging
from abc import abstractmethod

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel

from src.common.decorators import log_method_noarg
from src.common.messages import Message, MessageType
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.elements.utility.layout_helpers import add_widget, empty_widget
from src.pyside_ext.layout import HBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACDataSource(ItemInSidePanelWithAutoConfig):
    def __init__(self):
        super().__init__()
        self.label_text = "Data Source:"
        self.handler_current_index_changed = None

    def post_init(self, name, parent_widget):
        self.name = name

        self.widget, self.layout = add_widget(
            parent=parent_widget,
            inner_layout_class=HBoxLayout,
        )
        self.layout.setContentsMargins(2, 2, 2, 2),
        self.layout.setSpacing(5),

        self.label, _ = add_widget(
            widget=QLabel(self.label_text, self.widget),
            outer_layout=self.layout,
        )

        self.combo_box, _ = add_widget(
            widget=QComboBox(self.widget),
            outer_layout=self.layout,
        )

        self.combo_box.currentIndexChanged.connect(self.on_index_changed)
        self.clear_alert()

    def get_kwargs(self):
        return {self.name: self.combo_box.currentText()}

    def configure(self, **kwargs):
        result_id = kwargs["result_id"]

        self.combo_box.clear()
        self.combo_box.addItems(DATA_MANAGER.get_all_available_data_labels(result_id))

        selected_text = kwargs[self.name]
        if selected_text is None:
            selected_text = "Auto"

        index = self.combo_box.findText(selected_text)
        if index != -1:
            self.combo_box.setCurrentIndex(index)
        else:
            logging.warning(f"Data source '{selected_text}' not found. Switching to 'Auto'.")
            self.combo_box.setCurrentIndex(0)

    @log_method_noarg
    def set_alert(self):
        set_stylesheet(self.combo_box, css(border="1px solid red"))

    @log_method_noarg
    def clear_alert(self):
        set_stylesheet(self.combo_box, css(border=Style.General.border_elevated))

    @log_method_noarg
    def on_index_changed(self):
        if self.handler_current_index_changed:
            self.handler_current_index_changed()
        self.on_recalculate()

    def set_handler_current_index_changed(self, handler):
        self.handler_current_index_changed = handler
