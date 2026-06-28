#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from typing import List

from PySide6.QtWidgets import QLabel

from src.common.decorators import log_method_noarg
from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.elements.utility.primitive_elements import NoScrollComboBox
from src.pyside_ext.layout import HBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACComboBox(ItemInSidePanelWithAutoConfig):
    def __init__(self, label_text: str, items: List[str]):
        super().__init__()
        self.label_text = label_text
        self.items = items
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
            widget=NoScrollComboBox(self.widget),
            outer_layout=self.layout,
        )

        self.combo_box.addItems(self.items)

        self.combo_box.currentIndexChanged.connect(self.on_index_changed)
        self.clear_alert()

    def get_kwargs(self):
        return {self.name: self.combo_box.currentText()}

    def configure(self, **kwargs):
        selected_text = kwargs[self.name]
        if selected_text is None:
            selected_text = self.items[0]

        index = self.combo_box.findText(selected_text)
        self.combo_box.setCurrentIndex(index)

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
