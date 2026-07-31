#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.

# VALIDATED

from src.common.decorators import log_method
from src.common.messages import Message, MessageType
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.button_large import LargeButton
from src.side_area_panel.blueprint.registry import PanelRegistry
from src.side_area_panel.modules.common.result.registry import RESULTS, get_unique_result_id
from src.side_area_panel.modules.registry import ModuleRegistry, ModuleRegistryItem, ModuleType
from src.side_area_panel.panels.base import BasePanel


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
        if getattr(module.ui_instance, "recalculate_on_create", False):
            module.ui_instance.recalculate()
        self.root_class.action_activate_panel_by_index(module.settings_stacked_widget_index)
