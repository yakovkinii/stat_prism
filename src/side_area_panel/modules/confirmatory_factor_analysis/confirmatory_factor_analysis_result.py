import attrs

from src.side_area_panel.modules.common.result.registry import BaseResult

CFA_DESCRIPTION = """
<h2> Confirmatory Factor Analysis (CFA) </h2>
<h3> Description </h3>
<div>
CFA tests a user-specified factor structure (user assigns variables to each factor). The model is fit and model fit
indices (e.g., chi-square, RMSEA, CFI, TLI), factor loadings, and factor correlations are reported.
</div>
<h3> Inputs </h3>
<div>
<b>Factor variables:</b> Observed variables for each factor.<br>
<b>Number of factors:</b> How many latent factors to extract.<br>
<b>Allow factor correlation:</b> Permit factors to correlate (oblique model).<br>
<b>Filters:</b> Data filters to apply.<br>
</div>
<br><b>Pattern (factor loadings):</b> direct effect of each factor on each variable. <br><b>Structure matrix:</b>
correlation of each variable with each factor (includes indirect effects if factors are correlated). <br>
For interpretation and assigning variables to factors, use the pattern (factor loadings) matrix.
"""


@attrs.define
class CFAStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    n_factors = attrs.field(default=None)
    allow_factor_correlation = attrs.field(default=None)


class CFAResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: CFAStudyConfig):
        super().__init__(unique_id)
        self.title = "Confirmatory Factor Analysis"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = CFAStudyConfig
        self.config: CFAStudyConfig = config
        self.needs_update: bool = False
        self.description = CFA_DESCRIPTION
        self.set_placeholder()
