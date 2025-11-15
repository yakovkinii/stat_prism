#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import TYPE_CHECKING

from src.common.decorators import log_method
from src.common.messages import Message, MessageType
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.button_large import LargeButton
from src.side_area_panel.blueprint.registry import PanelRegistry
from src.side_area_panel.modules.common.result.registry import (
    RESULTS,
    get_unique_result_id,
)
from src.side_area_panel.modules.registry import (
    ModuleRegistry,
    ModuleRegistryItem,
    ModuleType,
)
from src.side_area_panel.panels.base import BasePanel

if TYPE_CHECKING:
    pass


class SelectDataProcessing(BasePanel):
    def setup_ui(self):
        self.elements = {}
        for module in ModuleRegistry:
            if module.value.module_type == ModuleType.DATA_PROCESSING:
                self.elements[module.name] = LargeButton(
                    label_text=module.value.display_name,
                    icon_path=module.value.icon_path,
                )

        self.caller_index = PanelRegistry.HOME.settings_stacked_widget_index
        self.setup(stretch=True, navigation_elements=True, ok_button=False, label="Data Processing")

    @log_method
    def handler(self, message: Message):
        if message.message_type != MessageType.CLICKED:
            super().handler(message)
            return

        module: ModuleRegistryItem = ModuleRegistry[message.caller_id].value

        result_id = get_unique_result_id()
        RESULTS[result_id] = module.result_class(
            unique_id=result_id,
            settings_panel_index=module.settings_stacked_widget_index,
            config=module.config_class(),
        )
        RESULTS[result_id].data = DATA_MANAGER.get_data_from_data_label(
            data_label="Auto",
            current_result_id=result_id,
    )
        DATA_MANAGER.add_data_to_chain(result_id=result_id)

        self.root_class.main_area_panel.add_data_processing(result_id=result_id)

        module.ui_instance.configure(result_id=result_id)
        self.root_class.action_activate_panel_by_index(module.settings_stacked_widget_index)
