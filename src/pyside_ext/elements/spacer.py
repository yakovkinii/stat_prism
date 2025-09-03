#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from PySide6.QtWidgets import QWidget

from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.styling import Style
from src.pyside_ext.styling import Style


class Spacer(BasePanelElement):
    def __init__(self):
        super().__init__()

    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.widget.setFixedHeight(Style.General.spacer_large.value)
