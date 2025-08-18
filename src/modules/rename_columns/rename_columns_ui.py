#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.decorators import log_method
from src.modules.base.base import BaseModulePanel
from src.modules.common.result.registry import RESULTS
from src.modules.rename_columns.result import RenameColumnsStudyConfig
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

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id
        self.config: RenameColumnsStudyConfig = RESULTS[result_id].config
        self.elements["renamer"].configure(self.config, result_id)
        self.configuring = False
