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


import json
import logging
import os
import tempfile
import zipfile

from PySide6 import QtWidgets

from src.common.decorators import log_method, log_method_noarg
from src.common.languages import LANGUAGE, Languages
from src.common.messages import MessageType
from src.common.theme import THEME, Themes
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.button_large import LargeButton
from src.savefile.autosave import autosave_dir
from src.savefile.json_store import load_project_json, reapply_element_settings
from src.savefile.versioning import IncompatibleProjectError, check_openable
from src.side_area_panel.blueprint.registry import PanelRegistry
from src.side_area_panel.modules.common.result.registry import RESULTS, get_unique_result_id
from src.side_area_panel.modules.registry import ModuleRegistry, ModuleType
from src.side_area_panel.panels.base import BasePanel


class HomeInitial(BasePanel):
    def setup_ui(self):
        self.elements = {
            "open": LargeButton(
                label_text="Open",
                icon_path="msc.folder-opened",
            ),
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
            "Supported Files (*.sp *.omv *.xlsx *.csv);;All Files (*)",
        )

        if not file_path:
            logging.info("No file selected")
            return

        try:
            self.load_file(file_path)
        except IncompatibleProjectError as error:
            QtWidgets.QMessageBox.warning(self.widget, "Cannot open project", str(error))

    @log_method
    def load_file(self, file_path):
        """Load a project (.sp) or raw data file (.omv/.xlsx/.csv). Shared by the Open button
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
                self._restore_json_project(temp_dir, self._read_meta(temp_dir))
            # Remember the project file so the next Save writes back to it (and the title bar
            # shows it).
            self.root_class.set_current_file_path(file_path)
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
            # A raw data import is not a project, so clear the path -> Save acts as Save As.
            self.root_class.set_current_file_path(None)

        # A freshly loaded project (or freshly imported file) has no unsaved changes yet,
        # even though building its cards marked the session dirty.
        self.root_class.clear_dirty()
        # The raw dataset was (re)established -> the crash-recovery snapshot must rewrite its parquet.
        self.root_class.autosave.mark_raw_changed()

        self.root_class.action_activate_panel_by_index(PanelRegistry.HOME.settings_stacked_widget_index)

    def _read_meta(self, directory) -> dict:
        meta_path = f"{directory}/meta.json"
        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _restore_json_project(self, directory, meta: dict, respect_auto_recalculate: bool = False):
        """Rebuild the session from an extracted JSON project directory -- shared by opening a .sp,
        crash recovery, and undo/redo. Refuses newer / legacy-pickle files, applies the saved theme &
        language before results render, routes each study to its module by config-object identity
        (a stable class, not a positional index) so adding/reordering modules never mis-routes a
        project, restores the raw dataset, then rebuilds the derived studies (only the raw dataset
        and configs are stored) and reapplies per-element display settings.

        With ``respect_auto_recalculate`` (undo/redo), the rebuild follows the Auto-recalculate
        setting -- data-processing always recomputes, analyses only when it is on (else they are
        marked stale) -- instead of forcing a full recompute the way opening a project does."""
        # Refuse projects saved by a newer, incompatible version (see savefile.versioning).
        check_openable(meta)

        # Legacy pickle projects (StatPrism <= 1.2.7) are no longer supported. 1.2.8 reads both
        # formats and saves JSON, so route the user through it to upgrade.
        if meta.get("storage") != "json":
            raise IncompatibleProjectError(
                "This project was saved in the old (pickle) format, which this version no "
                "longer opens. Open it in StatPrism 1.2.8 and use File > Save to convert it "
                "to the current format, then open it here."
            )

        if meta:
            self._apply_project_meta(meta)

        config_to_module = {
            module.value.config_class: module.value
            for module in ModuleRegistry
            if module.value.config_class is not None
        }
        add_by_type = {
            ModuleType.RAW_DATA: self.root_class.main_area_panel.add_raw_data,
            ModuleType.DATA_PROCESSING: self.root_class.main_area_panel.add_data_processing,
            ModuleType.DATA_ANALYSIS: self.root_class.main_area_panel.add_data_analysis,
        }

        results, raw_data_result_id, data_chain = load_project_json(directory, meta.get("version"))
        for result in results.values():
            module = config_to_module.get(type(result.config))
            if module is None:
                logging.warning("Skipping study with unknown config %s", type(result.config))
                continue
            result.settings_panel_index = module.settings_stacked_widget_index
            RESULTS[result.unique_id] = result
            add_by_type[module.module_type](result.unique_id)
        DATA_MANAGER.raw_data_result_id = raw_data_result_id
        DATA_MANAGER.data_chain = list(data_chain)

        main_area = self.root_class.main_area_panel
        if respect_auto_recalculate and not main_area.auto_recalculate:
            main_area.mark_all_stale()
        else:
            main_area.recompute_all()
        for result in list(RESULTS.values()):
            if reapply_element_settings(result):
                main_area.refresh_result(result_id=result.unique_id)

    def restore_snapshot_from_autosave(self):
        """Reload the current session from the autosave snapshot on disk (used by undo/redo). Unlike
        opening a project it honors Auto-recalculate on the rebuild and keeps the current file path
        (undo changes the session, so it stays unsaved)."""
        directory = str(autosave_dir())
        meta = self._read_meta(directory)
        self.root_class.main_area_panel.clear_all()
        self._restore_json_project(directory, meta, respect_auto_recalculate=True)
        self.root_class.mark_dirty()
        self.root_class.action_activate_panel_by_index(PanelRegistry.HOME.settings_stacked_widget_index)

    def recover_autosave(self):
        """Restore the crash-recovery snapshot into a live session. The restored work is marked
        unsaved (it postdates the last real save), and Save targets the original project file when
        the snapshot recorded one."""
        directory = str(autosave_dir())
        meta = self._read_meta(directory)
        self.root_class.main_area_panel.clear_all()
        self._restore_json_project(directory, meta)
        self.root_class.set_current_file_path(meta.get("source_path"))
        # Recovered work has not been saved to a real project file yet.
        self.root_class.mark_dirty()
        self.root_class.autosave.mark_raw_changed()
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
            elif message.caller_id == "about":
                PanelRegistry.HOME.ui_instance.about_handler()
                return
        return super().handler(message)
