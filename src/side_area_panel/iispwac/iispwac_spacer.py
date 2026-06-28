#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from PySide6.QtWidgets import QWidget

from src.common.decorators import log_method_noarg
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
