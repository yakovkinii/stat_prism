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

from enum import Enum

import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


class ClusterMethod(Enum):
    HIERARCHICAL = "Hierarchical"
    KMEANS = "KMeans"

    @staticmethod
    def get_values():
        return [e.value for e in ClusterMethod]


@attrs.define
class ClusterAnalysisConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    method = attrs.field(default=None)
    linkage = attrs.field(default=None)
    n_clusters = attrs.field(default=None)
    standardize = attrs.field(default=None)
    plots = attrs.field(default=None)
    show_assignments = attrs.field(default=None)
    verbal_indicators = attrs.field(default=None)
    interpretation = attrs.field(default=None)


class ClusterAnalysisResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ClusterAnalysisConfig):
        super().__init__(unique_id)
        self.title = "Cluster Analysis"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = ClusterAnalysisConfig
        self.config: ClusterAnalysisConfig = config
        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("cluster.description")
            + HTML.hr()
            + HTML.div(t("cluster_analysis.fine_print"), font_size=Style.FontSize.smaller)
        )
