#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import TYPE_CHECKING

from src.common.constant import SettingsPanelSize
from src.common.decorators import log_method
from src.common.messages import Message, MessageType
from src.modules.common.result.html_result import HTMLTableV2
from src.modules.common.result.registry import RESULTS
from src.pyside_ext.elements.tab import Tab
from src.settings_panel.panels.base import BasePanel

if TYPE_CHECKING:
    pass


class ResultItemSettingsV2(BasePanel):
    def setup_ui(self):
        self.elements = {
            "tab": Tab(),
        }
        self.setup(stretch=False, label="Settings")

    @log_method
    def configure(self, result_id, element_id):
        self.configuring = True
        self.result_id = result_id
        self.element_id = element_id
        self.result_element: HTMLTableV2 = RESULTS[result_id].result_elements[element_id]

        self.elements["tab"].clear_elements_soft()

        self.settings = self.result_element.display_settings
        for name, setting in self.settings.items():
            setting.inject(parent_widget=self.elements["tab"].widget, handler=self.handler, element_id=str(element_id))
            setting.setup()
            self.elements["tab"].add_element(name, setting)

        self.elements["tab"].widget.setFixedWidth(SettingsPanelSize.tab_width)
        self.configuring = False

    @log_method
    def handler(self, message: Message):
        if self.configuring:
            return
        if message.message_type in [MessageType.EDITING_FINISHED, MessageType.STATE_CHANGED]:
            self.root_class.main_area_panel.refresh_result(self.result_id, self.element_id)
            return
        super().handler(message)
