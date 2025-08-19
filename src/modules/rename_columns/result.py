#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from src.modules.common.result.registry import BaseResult


class RenameColumnsStudyConfig:
    def __init__(self, data=None, renamed_columns=None):
        from src.data.data_manager import DATA_MANAGER

        if data is None:
            data = DATA_MANAGER.get_latest_data()
        self.data = data
        if renamed_columns is None:
            renamed_columns = {}
        self.renamed_columns = renamed_columns


class RenameColumnsResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: RenameColumnsStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Rename Columns"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config: RenameColumnsStudyConfig = config
        self.needs_update: bool = False
        self.description = self._make_description()

    def _make_description(self):
        lines = []
        for old, new in self.config.renamed_columns.items():
            if old != new:
                lines.append(f"“{old}” → “{new}”")
        return "\n".join(lines)

    def update_description(self):
        self.description = self._make_description()
