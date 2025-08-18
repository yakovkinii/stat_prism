#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.decorators import log_method
from src.common.messages import Message, MessageType
from src.modules.base.base import BaseModulePanel
from src.modules.common.result.registry import RESULTS
from src.modules.rename_columns.result import RenameColumnsStudyConfig, RenameColumnsResult
from src.settings_panel.panels.renamer import Renamer
from src.pyside_ext.elements.spacer_small import SpacerSmall
from src.pyside_ext.elements.title import Title


class RenameColumns(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Rename Columns"),
            "spacer": SpacerSmall(),
            "renamer": Renamer(),
        }
        self.setup(stretch=True)
        self.elements["renamer"].inject(self.widget, self.handler, "renamer")

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id
        self.config: RenameColumnsStudyConfig = RESULTS[result_id].config
        self.elements["renamer"].configure(self.config, result_id)
        self.configuring = False

    @log_method
    def handler(self, message):
        if self.configuring:
            return
        if message.message_type == MessageType.EDITING_FINISHED and message.caller_id == "renamer":
            renamed_columns = message.payload.get("renamed_columns", {})
            self.config.renamed_columns = dict(renamed_columns)
            # Actually rename in data
            for idx, col in enumerate(self.config.data.columns):
                orig_name = col.column_name
                new_name = renamed_columns.get(orig_name, orig_name)
                col.column_name = new_name
            self.config.data.update_lookups()
            # Update result description
            result: RenameColumnsResult = RESULTS[self.result_id]
            result.update_description()
            result.needs_update = True
            self.root_class.main_area_panel.refresh_result(self.result_id)
            return
        super().handler(message)
