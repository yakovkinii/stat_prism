#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum

import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


class RotationType(Enum):
    NONE = "none"
    VARIMAX = "varimax"
    PROMAX = "promax (obl)"
    OBLIMIN = "oblimin (obl)"
    OBLIMAX = "oblimax"
    QUARTIMIN = "quartimin (obl)"
    QUARTIMAX = "quartimax"
    EQUAMAX = "equamax"

    @staticmethod
    def get_values():
        return [e.value for e in RotationType]


class ExtractionMethod(Enum):
    MINRES = "Minimum Residual (MINRES)"
    ML = "Maximum Likelihood (ML)"
    PRINCIPAL = "Principal Axis (PAF)"

    @staticmethod
    def get_values():
        return [e.value for e in ExtractionMethod]


@attrs.define
class FactorAnalysisStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    method = attrs.field(default=None)
    rotation = attrs.field(default=None)
    n_factors = attrs.field(default=None)
    kaiser_normalization = attrs.field(default=None)
    plots = attrs.field(default=None)
    number_columns = attrs.field(default=None)


class FactorAnalysisResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: FactorAnalysisStudyConfig):
        super().__init__(unique_id)
        self.title = "Exploratory Factor Analysis"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = FactorAnalysisStudyConfig
        self.config: FactorAnalysisStudyConfig = config
        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("efa.description")
            + HTML.hr()
            + HTML.div(t("exploratory_factor_analysis.fine_print"), font_size=Style.FontSize.smaller)
        )
