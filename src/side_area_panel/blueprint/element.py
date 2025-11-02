#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from abc import abstractmethod
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QTextEdit, QLineEdit


class ItemInSidePanelWithAutoConfig:
    def __init__(self):
        self.widget = ...
        self.label = ...

    # handler methods should be set with set_handler_{event_name} methods
    @abstractmethod
    def post_init(self, label, parent_widget):
        # Here, actual widgets are created
        pass

    @abstractmethod
    def get_kwargs(self):
        # To construct a config entry
        pass

    @abstractmethod
    def configure(self, **kwargs):
        # To configure the element based on config entry
        pass


class ItemInSidePanelWithAutoConfigHolder:
    def complete_init_of_items(self, parent_widget, parent_layout, stretch=True):
        cls = self.__class__
        items = {k: v for k, v in vars(cls).items() if not k.startswith("_") and not callable(v)}

        for label, item in items.items():
            item.post_init(label=label, parent_widget=parent_widget)
            parent_layout.addWidget(item.widget)
        if stretch:
            parent_layout.addStretch()


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
