#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from enum import Enum

import attrs

from src.side_area_panel.modules.common.result.registry import BaseResult

from .constant import DESCRIPTION


class ClusterMethod(Enum):
    KMEANS = "KMeans"

    @staticmethod
    def get_values():
        return [e.value for e in ClusterMethod]


@attrs.define
class ClusterAnalysisConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    method = attrs.field(default=None)
    n_clusters = attrs.field(default=None)
    filters = attrs.field(default=None)


class ClusterAnalysisResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ClusterAnalysisConfig):
        super().__init__(unique_id)
        self.title = "Cluster Analysis"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = ClusterAnalysisConfig
        self.config: ClusterAnalysisConfig = config
        self.needs_update: bool = False
        self.description = DESCRIPTION
        self.set_placeholder()
