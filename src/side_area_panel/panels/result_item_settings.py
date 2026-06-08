#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import TYPE_CHECKING

from PySide6 import QtCore

from src.common.constant import SettingsPanelSize
from src.common.decorators import log_method
from src.common.messages import Message, MessageType
from src.common.ui_constructor import create_tool_button_qta
from src.pyside_ext.elements.tab import Tab
from src.side_area_panel.modules.common.result.html_result import HTMLTableV2
from src.side_area_panel.modules.common.result.registry import RESULTS
from src.side_area_panel.panels.base import BasePanel

if TYPE_CHECKING:
    pass


class ResultItemSettingsV2(BasePanel):
    def setup_ui(self):
        self.elements = {
            "tab": Tab(),
        }
        self.setup(stretch=False, label="Settings")

        # "Reset to defaults" lives in the navigation bar; only shown for elements that
        # support it (plots). Inserted before the stretch so it sits next to back/ok.
        self._reset_button = create_tool_button_qta(
            parent=self.widget,
            icon_path="mdi6.restart",
            icon_size=QtCore.QSize(40, 40),
        )
        self._reset_button.setToolTip("Reset to default")
        self._reset_button.clicked.connect(self.reset_element)
        self._navigation_widget_layout.insertWidget(2, self._reset_button)
        self._reset_button.hide()

    @log_method
    def configure(self, result_id, element_id):
        self.configuring = True
        self.result_id = result_id
        self.element_id = element_id
        self.result_element: HTMLTableV2 = RESULTS[result_id].result_elements[element_id]
        self._reset_button.setVisible(hasattr(self.result_element, "reset_to_defaults"))

        self.elements["tab"].clear_elements_soft()

        self.settings = self.result_element.display_settings
        for name, setting in self.settings.items():
            setting.inject(parent_widget=self.elements["tab"].widget, handler=self.handler, element_id=str(element_id))
            setting.setup()
            self.elements["tab"].add_element(name, setting)

        self.elements["tab"].widget.setFixedWidth(SettingsPanelSize.tab_width)
        self.configuring = False

    @log_method
    def reset_element(self):
        if not hasattr(self.result_element, "reset_to_defaults"):
            return
        self.result_element.reset_to_defaults()
        # Re-render the plot, then rebuild the settings widgets so they show defaults.
        self.root_class.main_area_panel.refresh_result(self.result_id, self.element_id)
        self.configure(self.result_id, self.element_id)

    @log_method
    def handler(self, message: Message):
        if self.configuring:
            return
        if message.message_type in [MessageType.EDITING_FINISHED, MessageType.STATE_CHANGED]:
            self.root_class.main_area_panel.refresh_result(self.result_id, self.element_id)
            return
        super().handler(message)
