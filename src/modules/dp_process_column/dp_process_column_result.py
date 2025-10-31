#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from src.modules.common.result.registry import BaseResult

from src.data.data_manager import DATA_MANAGER


class ProcessColumnStudyConfig:
    def __init__(self, data=None, column=None, rename=""):
        if data is None:
            data = DATA_MANAGER.get_latest_data()
        self.data = data
        self.column = column
        self.rename = rename


class ProcessColumnResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ProcessColumnStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Process Column"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config: ProcessColumnStudyConfig = config
        self.needs_update: bool = False
        self.description = self._make_description()

    def _make_description(self):
        lines = []
        lines.append(f"Processed column: “{self.config.column}”")
        if self.config.rename and self.config.rename != self.config.column:
            lines.append(f'Renamed to: “{self.config.rename}”')
        return "\n".join(lines)

    def update_description(self):
        self.description = self._make_description()
