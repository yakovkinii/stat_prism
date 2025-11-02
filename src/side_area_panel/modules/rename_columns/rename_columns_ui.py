#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging

from src.common.decorators import log_method
from src.common.messages import MessageType
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.result.registry import RESULTS
from src.side_area_panel.modules.rename_columns.result import (
    RenameColumnsResult,
    RenameColumnsStudyConfig,
)
from src.side_area_panel.panels.renamer import Renamer


class RenameColumns(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "renamer": Renamer(),
        }
        self.setup(stretch=True, label="Rename Columns")
        self.elements["renamer"].inject(self.widget, self.handler, "renamer")

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id
        self.config: RenameColumnsStudyConfig = RESULTS[result_id].config
        self.elements["renamer"].configure(
            original_names=DATA_MANAGER.get_data_before_result_id(self.result_id).column_names(),
            current_renamed=self.config.renamed_columns.copy(),
        )
        self.configuring = False

    @log_method
    def handler(self, message):
        if self.configuring:
            return
        if message.message_type == MessageType.EDITING_FINISHED and message.caller_id == "renamer":
            returned_renamed_columns = message.payload.get("renamed_columns", {})
            renamed_columns = {}
            for from_name, to_name in returned_renamed_columns.items():
                if from_name == to_name:
                    logging.warning(f"Column '{from_name}' was renamed to itself, skipping.")
                    continue
                if to_name == "":
                    logging.warning(f"Column '{from_name}' was renamed to an empty string, skipping.")
                    continue
                if to_name in DATA_MANAGER.get_data_before_result_id(self.result_id).column_names():
                    logging.warning(
                        f"Column '{to_name}' already exists, skipping renaming from '{from_name}' to '{to_name}'."
                    )
                    continue
                renamed_columns[from_name] = to_name
            logging.info(f"Renaming columns: {renamed_columns}")

            # update all results

            for from_name, to_name in self.config.renamed_columns.items():
                for res in RESULTS.values():
                    logging.info(f"back-Renaming column '{to_name}' to '{from_name}' in result {res.unique_id}")
                    res.rename_column(
                        old_name=to_name,
                        new_name=from_name,
                    )

            for from_name, to_name in renamed_columns.items():
                for res in RESULTS.values():
                    logging.info(f"Renaming column '{from_name}' to '{to_name}' in result {res.unique_id}")
                    res.rename_column(
                        old_name=from_name,
                        new_name=to_name,
                    )

            # Actually rename in data
            raise NotImplementedError()
            self.config.data = DATA_MANAGER.get_data_before_result_id(self.result_id).copy()

            for idx, col in enumerate(self.config.data.columns):
                orig_name = col.column_name
                new_name = renamed_columns.get(orig_name, orig_name)
                col.column_name = new_name
            self.config.data.update_lookups()

            self.config.renamed_columns = dict(renamed_columns)
            # Update result description
            result: RenameColumnsResult = RESULTS[self.result_id]
            result.update_description()
            result.needs_update = True

            self.root_class.main_area_panel.refresh_result(self.result_id)
            self.configure(result_id=self.result_id)
            return
        super().handler(message)
