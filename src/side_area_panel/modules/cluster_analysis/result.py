#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from enum import Enum
from typing import List

from src.pyside_ext.elements.filter import FilterSettings
from src.side_area_panel.modules.common.result.registry import BaseResult

from .constant import DESCRIPTION


class ClusterMethod(Enum):
    KMEANS = "KMeans"

    @staticmethod
    def get_values():
        return [e.value for e in ClusterMethod]


class ClusterAnalysisConfig:
    def __init__(
        self,
        columns: List[str] = None,
        n_clusters: int = 2,
        method: ClusterMethod = ClusterMethod.KMEANS,
        filters: List[FilterSettings] = None,
    ):
        self.columns: List[str] = columns if columns is not None else []
        self.n_clusters: int = n_clusters
        self.method: ClusterMethod = method
        self.filters: List[FilterSettings] = filters if filters is not None else []


class ClusterAnalysisResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ClusterAnalysisConfig):
        super().__init__(unique_id)
        self.title = "Cluster Analysis"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config: ClusterAnalysisConfig = config
        self.needs_update: bool = False
        self.description = DESCRIPTION
        self.set_placeholder()

    def rename_column(self, old_name, new_name):
        if old_name in self.config.columns:
            idx = self.config.columns.index(old_name)
            self.config.columns[idx] = new_name
