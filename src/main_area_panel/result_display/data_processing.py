#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from PySide6.QtWidgets import QPushButton, QVBoxLayout

from src.common.elements.utility.layout_helpers import empty_widget, widget_in_layout
from src.data.data_manager import DATA_MANAGER
from src.data_viewer.data_viewer import view_data_popup
from src.main_area_panel.result_display.base import BaseResultDisplay
from src.main_area_panel.result_display.elements.result_label import ResultLabel
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class DataProcessingResultDisplay(BaseResultDisplay):
    def __init__(self, parent_widget, parent_class, root_class, label_text: str, data_item_index: int):
        super().__init__(parent_widget, parent_class, root_class)
        self.data_item_index = data_item_index

        self.widget, self.layout = empty_widget(
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda w, l: [
                l.setContentsMargins(10, 10, 0, 0),
                l.setSpacing(10),
            ],
        )
        set_stylesheet(
            self.widget,
            css(
                background_color=Style.Color.Background,
                border_left=Style.General.border_data_processing,
            ),
        )

        self.label = widget_in_layout(
            widget=ResultLabel(parent=self.widget, label_text=label_text),
            layout=self.layout,
        )

        self.popup_button = widget_in_layout(
            widget=QPushButton("View Data"),
            layout=self.layout,
            setup=lambda w, l: [
                w.clicked.connect(
                    lambda: view_data_popup(
                        root_class=self.root_class,
                        data=DATA_MANAGER.get_data_item(index=self.data_item_index),
                    )
                )
            ],
        )

    def activate_result(self, result_id, result_element_id):
        self.parent_class.activate_result(result_id, result_element_id)
