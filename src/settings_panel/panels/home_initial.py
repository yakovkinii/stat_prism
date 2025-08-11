#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import TYPE_CHECKING

from src.common.decorators import log_method
from src.common.messages import MessageType
from src.modules.common.result.registry import RESULTS, get_unique_result_id
from src.modules.registry import ModuleRegistry
from src.pyside_ext.elements.button_large import LargeButton
from src.pyside_ext.elements.spacer import Spacer
from src.settings_panel.panels.base import BasePanel
from src.settings_panel.registry import PanelRegistry

if TYPE_CHECKING:
    pass


class HomeInitial(BasePanel):
    def setup_ui(self):
        self.elements = {
            "open_sample": LargeButton(
                label_text="Open Sample Data",
                icon_path="msc.folder-opened",
            ),
            "open": LargeButton(
                label_text="Open",
                icon_path="msc.folder-opened",
            ),
            "spacer": Spacer(),
            "about": LargeButton(
                label_text="About",
                icon_path="ri.questionnaire-line",
            ),
        }

        self.setup(stretch=True)

    @log_method
    def handler(self, message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "open":
                module = ModuleRegistry.RAW_DATA.value

                result_id = get_unique_result_id()
                RESULTS[result_id] = module.result_class(
                    unique_id=result_id,
                    settings_panel_index=module.settings_stacked_widget_index,
                    config=module.config_class(),
                )
                self.root_class.main_area_panel.add_raw_data(result_id=result_id)
                module.ui_instance.configure(result_id=result_id)
                ModuleRegistry.RAW_DATA.ui_instance.open_handler()
                self.root_class.action_activate_panel_by_index(PanelRegistry.HOME.settings_stacked_widget_index)
                return
            elif message.caller_id == "open_sample":
                module = ModuleRegistry.RAW_DATA.value

                result_id = get_unique_result_id()
                RESULTS[result_id] = module.result_class(
                    unique_id=result_id,
                    settings_panel_index=module.settings_stacked_widget_index,
                    config=module.config_class(),
                )
                self.root_class.main_area_panel.add_raw_data(result_id=result_id)
                module.ui_instance.configure(result_id=result_id)
                ModuleRegistry.RAW_DATA.ui_instance.open_file("./data.csv")
                self.root_class.action_activate_panel_by_index(PanelRegistry.HOME.settings_stacked_widget_index)
                return
            elif message.caller_id == "about":
                PanelRegistry.HOME.ui_instance.about_handler()
                return
        return super().handler(message)
