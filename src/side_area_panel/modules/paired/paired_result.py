#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class PairedStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    method = attrs.field(default=None)
    assumption_checks = attrs.field(default=None)
    effect_size = attrs.field(default=None)
    verbal_indicators = attrs.field(default=None)
    plots = attrs.field(default=None)


# Fine-print on the exact methodology this module uses. English only by design (only
# reports / tables are localised), rendered smaller under the general description so the
# chosen conventions are explicit and auditable.
_ASSUMPTIONS_FINE_PRINT_EN = (
    "<b>Methodology &amp; assumptions</b>"
    "<ul>"
    "<li><b>Design.</b> The selected variables are treated as repeated measurements of a "
    "single within-subject factor (e.g. time points or conditions on the same respondents). "
    "Only complete cases are used &mdash; a respondent missing any condition is dropped "
    "(listwise).</li>"
    "<li><b>Test selection.</b> Two conditions use the paired-samples family; three or more "
    "use the repeated-measures family. Parametric tests are used when the normality check "
    "passes; otherwise the non-parametric equivalents are used.</li>"
    "<li><b>Normality.</b> Shapiro&ndash;Wilk. For two conditions it is computed on the "
    "paired differences; for three or more it is computed per condition. The data are treated "
    "as normal only when every check passes (p &gt; .05).</li>"
    "<li><b>Parametric, 2 conditions.</b> Paired-samples t-test; effect size Cohen&rsquo;s "
    "d<sub>z</sub> = mean(difference) / SD(difference).</li>"
    "<li><b>Parametric, 3+ conditions.</b> One-way repeated-measures ANOVA; effect size "
    "generalised &eta;&sup2;<sub>G</sub>. Sphericity is tested with Mauchly&rsquo;s test and "
    "the Greenhouse&ndash;Geisser&ndash;corrected p-value (with &epsilon;) is reported "
    "alongside the uncorrected one.</li>"
    "<li><b>Non-parametric, 2 conditions.</b> Wilcoxon signed-rank test; effect size the "
    "matched-pairs rank-biserial correlation.</li>"
    "<li><b>Non-parametric, 3+ conditions.</b> Friedman test; effect size Kendall&rsquo;s "
    "W.</li>"
    "<li><b>Post-hoc</b> (only when &lsquo;Effect size / Post-hoc&rsquo; is on, three or more "
    "conditions, and the omnibus test is significant): parametric &rarr; pairwise paired "
    "t-tests with Holm correction; non-parametric &rarr; Nemenyi test.</li>"
    "<li><b>Verbal indicators.</b> &lsquo;Verbal indicators in tables&rsquo; adds plain-language "
    "columns next to each p-value (Significant? / Normal? at &alpha; = .05) and a Magnitude "
    "column for the effect size (Cohen&rsquo;s d by |d| 0.2 / 0.5 / 0.8; the rank-biserial r "
    "by the correlation bands |r| .1 / .3 / .5).</li>"
    "<li><b>Threshold.</b> All tests are two-sided and use &alpha; = .05.</li>"
    "</ul>"
)


class PairedResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: PairedStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Paired/Repeated Measures"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = PairedStudyConfig
        self.config: PairedStudyConfig = config

        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("paired.description")
            + HTML.hr()
            + HTML.div(_ASSUMPTIONS_FINE_PRINT_EN, font_size=Style.FontSize.smaller)
        )
