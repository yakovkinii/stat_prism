from enum import Enum
from typing import List

from src.modules.common.result.registry import BaseResult
from src.modules.exploratory_factor_analysis.constant import DESCRIPTION
from src.pyside_ext.elements.filter import FilterSettings


class RotationType(Enum):
    NONE = "none"
    VARIMAX = "varimax"
    QUARTIMAX = "quartimax"
    EQUAMAX = "equamax"
    PROMAX = "promax"   # oblique
    OBLIMIN = "oblimin" # oblique
    GEOMIN = "geomin"   # oblique
    @staticmethod
    def get_values():
        return [e.value for e in RotationType]

class ExtractionMethod(Enum):
    ML = "maximum_likelihood"
    PRINCIPAL = "principal_axis"

    @staticmethod
    def get_values():
        return [e.value for e in ExtractionMethod]

class FactorAnalysisStudyConfig:
    def __init__(
        self,
        columns: List[str] = None,
        n_factors: int = 2,
        rotation: RotationType = RotationType.VARIMAX,
        method: ExtractionMethod = ExtractionMethod.ML,
        kaiser_normalization: bool = True,
        filters: List[FilterSettings] = None,
    ):
        self.columns: List[str] = columns if columns is not None else []
        self.n_factors: int = n_factors
        self.rotation: RotationType = rotation
        self.method: ExtractionMethod = method
        self.kaiser_normalization: bool = kaiser_normalization
        self.filters: List[FilterSettings] = filters if filters is not None else []


class FactorAnalysisResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: FactorAnalysisStudyConfig):
        super().__init__(unique_id)
        self.title = "Exploratory Factor Analysis"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config: FactorAnalysisStudyConfig = config
        self.needs_update: bool = False
        self.description = DESCRIPTION
        self.set_placeholder()

    def rename_column(self, old_name, new_name):
        # Update references in config
        if old_name in self.config.columns:
            idx = self.config.columns.index(old_name)
            self.config.columns[idx] = new_name
