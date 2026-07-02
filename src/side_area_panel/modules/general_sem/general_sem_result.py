#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import attrs

from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult

_DESCRIPTION = (
    "A <b>structural equation model (SEM)</b> tests a whole network of relationships at once. "
    "It has two layers. The <b>measurement model</b> defines <i>latent factors</i> — traits you "
    "can't measure directly (e.g. <i>motivation</i>) — from the observed columns (questionnaire "
    "items) you assign as their indicators. The <b>structural model</b> is the set of "
    "<b>paths</b> you draw between those factors (and/or observed variables): which one is "
    "expected to influence which. semopy then estimates every path's strength simultaneously and "
    "reports how well the whole model fits the data."
)

_FINE_PRINT = (
    "<b>The two path types</b><br>"
    "• <b>predicts (→) = <code>~</code></b> — a directed effect: <i>From</i> is a predictor of "
    "<i>To</i>, like a regression (<code>To ~ From</code>). Several <code>predicts</code> rows "
    "into the same target combine into one regression (<code>Y ~ X1 + X2</code>), so each estimate "
    "is that predictor's <i>unique</i> effect, controlling for the others.<br>"
    "• <b>covaries (↔) = <code>~~</code></b> — a symmetric association, no direction: the two share "
    "variance without either causing the other.<br>"
    "<br><b>What is fixed by default</b> (before you add any path)<br>"
    "• <b>factor ↔ factor</b> — automatically <b>free to correlate</b>, so adding a ↔ between two "
    "factors is redundant.<br>"
    "• <b>item ↔ item</b> — forced <b>independent</b> (their residual covariance is fixed at 0); add "
    "a ↔ to free it — a <i>correlated residual</i> (items sharing wording/method variance).<br>"
    "• <b>factor → its own item</b> — a <b>loading</b>, created directed simply by assigning the "
    "item to the factor (the trait is real, the item a noisy symptom of it).<br>"
    "• <b>factor and another factor's item</b> — <b>no direct link</b> by default (fixed at 0); they "
    "relate only indirectly through the factor↔factor correlation. A direct arrow here is a "
    "<b>cross-loading</b> — <i>directed</i> (factor → item), not ↔.<br>"
    "<br>So the reason to add a path is to assert <b>direction</b> (→) where there was only "
    "correlation — turning “Motivation and Performance are related” into “Motivation drives "
    "Performance”, or chaining <code>A → B → C</code> (mediation), which a plain ↔ cannot express. "
    "Also valid: an item → a factor (a MIMIC-style observed cause). Ignored as degenerate: a "
    "self-loop, and a factor → its own indicator (already a loading).<br>"
    "<br><b>Reading the estimates</b><br>"
    "The → and ↔ paths are the interesting rows. A <code>var(x)</code> row is just a <b>variance</b> "
    "(the 2nd central moment, in the data's own units — generally <i>not</i> 1; the standardized "
    "column reports it as 1). For an item it is the <b>leftover / error variance</b>; only its "
    "standardized value is really informative — it equals the unexplained proportion "
    "(1 − R²), so 0.3 means 70% of the item is explained by its factor. The raw number itself is "
    "rarely interpreted. Why model latent factors at all? The → paths are estimated between the "
    "<b>error-free</b> traits, not the noisy items, so effects aren't attenuated by measurement "
    "error. Every estimate has a standard error, <i>p</i>-value and standardized value; the fit "
    "table gives the global indices (χ², CFI, TLI, RMSEA, …). Fitted with the <b>semopy</b> backend "
    "on complete numeric rows (list-wise deletion)."
)


@attrs.define
class GeneralSEMStudyConfig:
    data_source = attrs.field(default=None)
    n_factors = attrs.field(default=None)
    column_selector = attrs.field(default=None)  # per-factor indicator lists (measurement model)
    factor_names = attrs.field(default=None)
    paths = attrs.field(default=None)  # [{"from": node, "to": node, "type": "~"|"~~"}, ...]
    estimator = attrs.field(default=None)
    verbal_indicators = attrs.field(default=None)
    interpretation = attrs.field(default=None)
    plots = attrs.field(default=None)


class GeneralSEMResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: GeneralSEMStudyConfig):
        super().__init__(unique_id)
        self.title = "Structural Equation Model"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = GeneralSEMStudyConfig
        self.config: GeneralSEMStudyConfig = config
        self.needs_update: bool = False
        # Full guide + methodology fine-print (smaller, below a rule); shown behind the info (i) button.
        self.description = _DESCRIPTION + HTML.hr() + HTML.div(_FINE_PRINT, font_size=Style.FontSize.smaller)
        self.set_placeholder()
