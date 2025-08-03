#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class BaseResultDisplay:
    def __init__(self, parent_widget, parent_class, root_class):
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        self.parent_widget = parent_widget

        self.widget = ...
        self.layout = ...
