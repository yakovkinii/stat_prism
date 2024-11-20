#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

from PySide6.QtWidgets import QWidget

from src.common.elements.base.base import BasePanelElement


class Spacer(BasePanelElement):
    def __init__(self):
        super().__init__()

    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.widget.setFixedHeight(40)
