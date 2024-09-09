from PySide6.QtWidgets import QGridLayout, QWidget

from src.common.elements.base.base import BasePanelElement


class SmallButtonContainer(BasePanelElement):
    def __init__(self, small_buttons):
        super().__init__()
        self.layout = None

        self.small_buttons = small_buttons

    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.layout = QGridLayout(self.widget)
        self.layout.setContentsMargins(20, 0, 20, 0)
        self.layout.setSpacing(10)
        self.widget.setLayout(self.layout)

        for i, small_button in enumerate(self.small_buttons.values()):
            self.layout.addWidget(small_button.widget, i // 2, i % 2)
