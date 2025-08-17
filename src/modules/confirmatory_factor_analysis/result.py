from enum import Enum
from typing import List

from src.modules.common.result.registry import BaseResult
from src.pyside_ext.elements.filter import FilterSettings

CFA_DESCRIPTION = """
<h2> Confirmatory Factor Analysis (CFA) </h2>
<h3> Description </h3>
<div>
CFA tests a user-specified factor structure (here: two factors, user assigns variables to each). The model is fit and model fit indices (e.g., chi-square, RMSEA, CFI, TLI), factor loadings, and factor correlations are reported.
</div>
<h3> Inputs </h3>
<div>
<b>Factor 1 variables:</b> Observed variables for Factor 1.<br>
<b>Factor 2 variables:</b> Observed variables for Factor 2.<br>
<b>Rotation:</b> (Optional) Rotation for factor loadings.<br>
<b>Filters:</b> Data filters to apply.<br>
</div>
"""

class RotationType(Enum):
    NONE = "none"
    OBLIMIN = "oblimin"
    # Add more if needed
    @staticmethod
    def get_values():
        return [e.value for e in RotationType]

class CFAStudyConfig:
    def __init__(
        self,
        columns_list: list = None,
        n_factors: int = 2,
        rotation: RotationType = RotationType.NONE,
        filters: List[FilterSettings] = None,
    ):
        self.columns_list: list = columns_list if columns_list is not None else [[] for _ in range(n_factors)]
        self.n_factors: int = n_factors
        self.rotation: RotationType = rotation
        self.filters: List[FilterSettings] = filters if filters is not None else []

class CFAResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: CFAStudyConfig):
        super().__init__(unique_id)
        self.title = "Confirmatory Factor Analysis"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config: CFAStudyConfig = config
        self.needs_update: bool = False
        self.description = CFA_DESCRIPTION
        self.set_placeholder()

    def rename_column(self, old_name, new_name):
        for factor_vars in self.config.columns_list:
            for i, col in enumerate(factor_vars):
                if col == old_name:
                    factor_vars[i] = new_name
