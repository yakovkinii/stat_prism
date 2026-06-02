#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging
import pickle
import tempfile
import zipfile
from typing import TYPE_CHECKING

from PySide6 import QtWidgets

from src.common.decorators import log_method, log_method_noarg
from src.common.messages import MessageType
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.button_large import LargeButton
from src.pyside_ext.elements.spacer import Spacer
from src.side_area_panel.blueprint.registry import PanelRegistry
from src.side_area_panel.modules.common.result.registry import (
    RESULTS,
    get_unique_result_id,
)
from src.side_area_panel.modules.registry import ModuleRegistry
from src.side_area_panel.panels.base import BasePanel

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

        self.setup(stretch=True, navigation_elements=False)

    @log_method_noarg
    def open_handler(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.widget,
            "Open File",
            "",
            "Supported Files (*.sp *.xlsx *.csv);;All Files (*)",
        )

        if not file_path:
            logging.info("No file selected")
            return

        if file_path.endswith(".sp"):
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(file_path, "r") as zipf:
                    zipf.extractall(temp_dir)

                RESULTS.clear()
                with open(f"{temp_dir}/results.pkl", "rb") as f:
                    results = pickle.load(f)
                    for result in results.values():
                        RESULTS[result.unique_id] = result
                        if result.settings_panel_index in [ModuleRegistry.RAW_DATA.settings_stacked_widget_index]:
                            self.root_class.main_area_panel.add_raw_data(result.unique_id)
                        elif result.settings_panel_index in [
                            ModuleRegistry.CALCULATE_SCALE.settings_stacked_widget_index,
                            ModuleRegistry.DP_PROCESS_COLUMN.settings_stacked_widget_index,
                            ModuleRegistry.INVERT_SCALE.settings_stacked_widget_index,
                        ]:
                            self.root_class.main_area_panel.add_data_processing(result.unique_id)
                        else:
                            self.root_class.main_area_panel.add_data_analysis(result.unique_id)

                with open(f"{temp_dir}/data_manager.pkl", "rb") as f:
                    data_manager = pickle.load(f)
                    DATA_MANAGER.from_unpickled(data_manager)

        else:
            module = ModuleRegistry.RAW_DATA.value

            result_id = get_unique_result_id()
            RESULTS[result_id] = module.result_class(
                unique_id=result_id,
                settings_panel_index=module.settings_stacked_widget_index,
                config=module.config_class(),
            )
            self.root_class.main_area_panel.add_raw_data(result_id=result_id)
            module.ui_instance.configure(result_id=result_id)
            ModuleRegistry.RAW_DATA.ui_instance.open_file(file_path)

        self.root_class.action_activate_panel_by_index(PanelRegistry.HOME.settings_stacked_widget_index)

    @log_method
    def handler(self, message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "open":
                return self.open_handler()
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
