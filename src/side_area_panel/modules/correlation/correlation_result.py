#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum

import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


class CorrelationType(Enum):
    PEARSON = 0
    SPEARMAN = 1
    KENDALL = 2
    PHI = 3
    TETRACHORIC = 4
    POLYCHORIC = 5
    KENDALL_C = 6


CORRELATION_TYPE_MAP = {
    "Pearson": CorrelationType.PEARSON,
    "Spearman": CorrelationType.SPEARMAN,
    "Kendall": CorrelationType.KENDALL,
    "Kendall tau c": CorrelationType.KENDALL_C,
    "Phi": CorrelationType.PHI,
    "Tetrachoric": CorrelationType.TETRACHORIC,
    "Polychoric": CorrelationType.POLYCHORIC,
}


@attrs.define
class CorrelationStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    correlation_type = attrs.field(default=None)
    compact = attrs.field(default=None)
    generate_heatmap = attrs.field(default=None)
    generate_plots = attrs.field(default=None)
    report_only_significant = attrs.field(default=None)


# Fine-print on the exact methodology / variants this module uses. English only by
# design (only reports/tables are localised), rendered in a smaller font under the
# general description so the chosen conventions are explicit and auditable.
_ASSUMPTIONS_FINE_PRINT_EN = (
    "<b>Methodology &amp; assumptions</b>"
    "<ul>"
    "<li><b>Coefficients &amp; p-values.</b>"
    "<ul>"
    "<li>Pearson&rsquo;s r &mdash; t-distribution p-value, df = n &minus; 2 (reported).</li>"
    "<li>Spearman&rsquo;s &rho; / Kendall&rsquo;s &tau; (tau-b) / &tau;<sub>c</sub> &mdash; "
    "p-values from SciPy; no df is reported.</li>"
    "<li>Phi &phi; &mdash; &radic;(&chi;<sup>2</sup>/N) from the 2&times;2 table; p-value from "
    "the chi-square test.</li>"
    "<li>Tetrachoric &mdash; maximum-likelihood estimate for a 2&times;2 table; Wald p-value "
    "(z = &rho;/SE), df = n &minus; 2. Returned blank when the pair is not 2&times;2.</li>"
    "<li>Polychoric &mdash; maximum-likelihood estimate; likelihood-ratio p-value (df = 1).</li>"
    "</ul></li>"
    "<li><b>Partial correlation.</b> If any &lsquo;Control for&rsquo; variables are given, the "
    "table shows <i>partial</i> correlations among the selected variables with the linear "
    "effect of the controls removed from both sides of each pair (Pearson or Spearman only; "
    "df = n &minus; 2 &minus; number of controls). Pairwise scatter plots are omitted in this "
    "mode, since the raw scatter would not reflect the partialled relationship.</li>"
    "<li><b>Missing data.</b> Pairwise deletion &mdash; each pair uses only rows where both "
    "variables are present.</li>"
    "<li><b>Ordinal variables.</b> Selected ordinal variables are mapped to numeric codes. "
    "Using Pearson&rsquo;s r on ordinal data triggers a warning (it assumes interval data).</li>"
    "<li><b>Reporting.</b> Significance stars: * p &lt; .05, ** p &lt; .01, *** p &lt; .001; "
    "the verbal summary uses &alpha; = .05. Strength of |r|: &gt; .5 strong, &gt; .3 moderate, "
    "&gt; .1 weak, otherwise very weak. All tests are two-sided.</li>"
    "</ul>"
)


class CorrelationResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: CorrelationStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Correlation"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = CorrelationStudyConfig
        self.config: CorrelationStudyConfig = config

        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("correlation.description")
            + HTML.hr()
            + HTML.div(_ASSUMPTIONS_FINE_PRINT_EN, font_size=Style.FontSize.smaller)
        )
