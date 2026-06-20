#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import json
import logging
import os
import pickle
import tempfile
import zipfile
from typing import TYPE_CHECKING

from PySide6 import QtWidgets

from src.common.decorators import log_method, log_method_noarg
from src.common.languages import LANGUAGE, Languages
from src.common.messages import MessageType
from src.common.theme import THEME, Themes
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.button_large import LargeButton
from src.pyside_ext.elements.spacer import Spacer
from src.side_area_panel.blueprint.registry import PanelRegistry
from src.side_area_panel.modules.common.result.registry import (
    RESULTS,
    get_unique_result_id,
)
from src.side_area_panel.modules.registry import ModuleRegistry, ModuleType
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
        if not self.root_class.confirm_discard_if_dirty():
            return
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.widget,
            "Open File",
            "",
            "Supported Files (*.sp *.xlsx *.csv);;All Files (*)",
        )

        if not file_path:
            logging.info("No file selected")
            return

        self.load_file(file_path)

    @log_method
    def load_file(self, file_path):
        """Load a project (.sp) or raw data file (.xlsx/.csv). Shared by the Open button
        and the command-line / file-association startup path (launcher -> ui_main)."""
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            logging.warning("File to load does not exist: %s", file_path)
            return

        # Tear down any existing session first, so opening never appends to / collides with
        # the previously loaded project.
        self.root_class.main_area_panel.clear_all()

        if file_path.endswith(".sp"):
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(file_path, "r") as zipf:
                    zipf.extractall(temp_dir)

                # Restore the saved theme & language before the results render, so they
                # appear in the project's look and language.
                meta_path = f"{temp_dir}/meta.json"
                if os.path.exists(meta_path):
                    with open(meta_path, encoding="utf-8") as f:
                        self._apply_project_meta(json.load(f))

                # Map each module's settings-panel index to its type, so a saved result is
                # routed to the right lane by module_type (no hand-maintained index lists).
                index_to_type = {
                    module.value.settings_stacked_widget_index: module.value.module_type
                    for module in ModuleRegistry
                }
                add_by_type = {
                    ModuleType.RAW_DATA: self.root_class.main_area_panel.add_raw_data,
                    ModuleType.DATA_PROCESSING: self.root_class.main_area_panel.add_data_processing,
                    ModuleType.DATA_ANALYSIS: self.root_class.main_area_panel.add_data_analysis,
                }

                with open(f"{temp_dir}/results.pkl", "rb") as f:
                    results = pickle.load(f)
                    for result in results.values():
                        RESULTS[result.unique_id] = result
                        module_type = index_to_type.get(result.settings_panel_index, ModuleType.DATA_ANALYSIS)
                        add_by_type[module_type](result.unique_id)

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

        # A freshly loaded project (or freshly imported file) has no unsaved changes yet,
        # even though building its cards marked the session dirty.
        self.root_class.clear_dirty()

        self.root_class.action_activate_panel_by_index(PanelRegistry.HOME.settings_stacked_widget_index)

    def _apply_project_meta(self, meta: dict):
        """Apply a loaded project's saved language & theme (and sync the menu ticks),
        without triggering a recompute -- the results render in this state next."""
        logging.info("Loading StatPrism project saved with version %s", meta.get("version"))
        settings_panel = self.root_class.settings_panel

        try:
            LANGUAGE.set_language(Languages(meta.get("language")))
        except ValueError:
            logging.warning("Unknown language in project meta: %s", meta.get("language"))
        settings_panel.en_action.setChecked(LANGUAGE.is_en())
        settings_panel.ua_action.setChecked(LANGUAGE.is_ua())

        try:
            theme = Themes(meta.get("theme"))
            THEME.set_theme(theme)
            for candidate, action in settings_panel.theme_actions.items():
                action.setChecked(candidate == theme)
        except ValueError:
            logging.warning("Unknown theme in project meta: %s", meta.get("theme"))

    @log_method
    def handler(self, message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "open":
                return self.open_handler()
            elif message.caller_id == "open_sample":
                self.root_class.main_area_panel.clear_all()
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
                self.root_class.clear_dirty()
                self.root_class.action_activate_panel_by_index(PanelRegistry.HOME.settings_stacked_widget_index)
                return
            elif message.caller_id == "about":
                PanelRegistry.HOME.ui_instance.about_handler()
                return
        return super().handler(message)
