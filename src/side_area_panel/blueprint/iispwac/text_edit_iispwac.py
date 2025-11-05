#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6.QtWidgets import QLineEdit

from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class TextEditIISPWAC(ItemInSidePanelWithAutoConfig):
    def post_init(self, label, parent_widget):
        self.label = label
        self.widget = QLineEdit(parent_widget)

    def get_kwargs(self):
        return {self.label: self.widget.text()}

    def configure(self, **kwargs):
        text = kwargs[self.label]
        self.widget.setText(text)

    def set_handler_editing_finished(self, handler):
        self.widget.editingFinished.connect(handler)

