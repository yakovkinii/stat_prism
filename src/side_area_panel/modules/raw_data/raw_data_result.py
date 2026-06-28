#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import pandas as pd

from src.side_area_panel.modules.common.result.registry import BaseResult


class RawDataStudyConfig:
    def __init__(
        self,
        dataframe: pd.DataFrame = None,
        path="",
        timestamp="",
        add_id=True,
        header_colors=None,
    ):
        self.dataframe = dataframe
        self.path = path
        self.timestamp = timestamp
        self.add_id = add_id
        # {column_name: '#rrggbb'} read from the source sheet's coloured header cells.
        self.header_colors = header_colors or {}


class RawDataResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: RawDataStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Raw Data"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config: RawDataStudyConfig = config

        self.needs_update: bool = False
        self.description = ""

        self.data = None
