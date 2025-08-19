#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum
from typing import List

from src.modules.common.result.registry import BaseResult
from src.modules.correlation.constant import DESCRIPTION
from src.pyside_ext.elements.filter import FilterSettings


class CorrelationType(Enum):
    PEARSON = 0
    SPEARMAN = 1
    KENDALL = 2
    PHI = 3
    TETRACHORIC = 4


CORRELATION_TYPE_MAP = {
    "Pearson": CorrelationType.PEARSON,
    "Spearman": CorrelationType.SPEARMAN,
    "Kendall": CorrelationType.KENDALL,
    "Phi": CorrelationType.PHI,
    "Tetrachoric": CorrelationType.TETRACHORIC,
}


class CorrelationStudyConfig:
    def __init__(
        self,
        selected_columns: List[str] = None,
        correlation_type: CorrelationType = CorrelationType.PEARSON,
        compact: bool = False,
        generate_heatmap: bool = False,
        generate_plots: bool = False,
        report_only_significant: bool = True,
        filters: List[FilterSettings] = None,
    ):
        self.selected_columns = selected_columns if selected_columns is not None else []
        self.compact = compact
        self.generate_heatmap = generate_heatmap
        self.generate_plots = generate_plots
        self.correlation_type = correlation_type
        self.report_only_significant = report_only_significant
        self.filters: List[FilterSettings] = filters if filters is not None else []


class CorrelationResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: CorrelationStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Correlation"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config: CorrelationStudyConfig = config

        self.needs_update: bool = False
        self.description = DESCRIPTION
        self.set_placeholder()

    def rename_column(self, old_name, new_name):
        self.config.selected_columns = [new_name if col == old_name else col for col in self.config.selected_columns]
        self.needs_update = True
