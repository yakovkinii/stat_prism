#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class CFAStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    n_factors = attrs.field(default=None)
    allow_factor_correlation = attrs.field(default=None)
    verbal_indicators = attrs.field(default=None)


# Fine-print on the exact methodology / variants this module uses. English only by
# design (only reports/tables are localised), rendered in a smaller font under the
# general description so the chosen conventions are explicit and auditable.
_ASSUMPTIONS_FINE_PRINT_EN = (
    "<b>Methodology &amp; assumptions</b>"
    "<ul>"
    "<li><b>Estimation.</b> Maximum-likelihood fit of the user-specified measurement model to "
    "the sample covariance matrix (rows with any missing value are dropped list-wise; ordinal "
    "items are scored numerically). Each factor's variance is fixed to 1 for identification, so "
    "every factor needs at least two indicators.</li>"
    "<li><b>Loadings.</b> Reported as the <i>standardised</i> solution, so each loading is the "
    "indicator&ndash;factor correlation (roughly in &minus;1..1) and is comparable across "
    "indicators. A negative loading just means an inverse (reverse-keyed) relationship; "
    "interpret its magnitude. Loadings are sign-normalised so each factor's dominant direction "
    "is positive.</li>"
    "<li><b>Fit indices.</b> <b>&chi;&sup2;</b> tests <i>exact</i> fit (non-significant = good, "
    "but it is sensitive to sample size). <b>RMSEA</b>: &lt; .05 close, &lt; .08 acceptable, "
    "&lt; .10 mediocre, otherwise poor. <b>CFI / TLI</b>: &ge; .95 excellent, &ge; .90 "
    "acceptable, otherwise poor. <b>SRMR</b>: &le; .08 good, otherwise poor. <b>df</b> are the "
    "model degrees of freedom.</li>"
    "<li><b>Factor correlations.</b> With &lsquo;Allow factor correlation&rsquo; the factors may "
    "correlate (oblique model) and a factor-correlation matrix (&Phi;) is reported; otherwise "
    "the factors are constrained orthogonal.</li>"
    "<li><b>Verbal indicators.</b> &lsquo;Verbal indicators in tables&rsquo; adds an "
    "Interpretation column to the fit-index table.</li>"
    "<li><b>Reproducibility.</b> Optimisation uses a fixed random seed, so re-running the same "
    "model gives the same solution. A non-convergence warning means the estimate may be "
    "unreliable.</li>"
    "</ul>"
)


class CFAResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: CFAStudyConfig):
        super().__init__(unique_id)
        self.title = "Confirmatory Factor Analysis"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = CFAStudyConfig
        self.config: CFAStudyConfig = config
        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("cfa.description")
            + HTML.hr()
            + HTML.div(_ASSUMPTIONS_FINE_PRINT_EN, font_size=Style.FontSize.smaller)
        )
