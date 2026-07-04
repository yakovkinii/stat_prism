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
