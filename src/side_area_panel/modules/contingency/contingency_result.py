#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class ContingencyStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    continuity_correction = attrs.field(default=None)
    effect_size = attrs.field(default=None)
    verbal_indicators = attrs.field(default=None)
    plots = attrs.field(default=None)


# Fine-print on the exact methodology / variants this module uses. English only by
# design (only reports/tables are localised), rendered in a smaller font under the
# general description so the chosen conventions are explicit and auditable.
_ASSUMPTIONS_FINE_PRINT_EN = (
    "<b>Methodology &amp; assumptions</b>"
    "<ul>"
    "<li><b>Test.</b> Pearson&rsquo;s chi-square test of independence on the cross-tabulation "
    "of the two variables.</li>"
    "<li><b>Continuity correction.</b> Yates&rsquo; correction only affects 2&times;2 tables. "
    "The &ldquo;Continuity correction&rdquo; switch (on by default) is applied consistently to "
    "<i>both</i> the reported &chi;<sup>2</sup> and the effect size. Note that effect sizes are "
    "conventionally computed from the <i>uncorrected</i> &chi;<sup>2</sup> &mdash; turn the "
    "switch off to follow that convention. For tables larger than 2&times;2 it has no effect.</li>"
    "<li><b>Effect size.</b> &phi; (phi) for 2&times;2 tables, Cramer&rsquo;s V otherwise, with "
    "V = &radic;(&chi;<sup>2</sup> / (N&middot;(min(r,c)&minus;1))). Interpretation thresholds: "
    "&lt; 0.2 weak, &lt; 0.6 moderate, otherwise strong.</li>"
    "<li><b>Verbal indicators.</b> &lsquo;Verbal indicators in tables&rsquo; adds a Significant? "
    "conclusion next to the &chi;<sup>2</sup> p-value and, when an effect size is shown, a "
    "Magnitude column (weak / moderate / strong by the thresholds above).</li>"
    "<li><b>Small samples.</b> The chi-square test assumes expected cell counts &ge; 5. For "
    "2&times;2 tables where this is violated, Fisher&rsquo;s exact test (two-sided) is reported "
    "instead; for larger tables a low-count chi-square should be interpreted with caution.</li>"
    "<li><b>Threshold.</b> Tests are two-sided and use &alpha; = .05.</li>"
    "<li><b>Missing data.</b> Rows with a missing value in either variable are excluded "
    "(pairwise).</li>"
    "</ul>"
)


class ContingencyResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ContingencyStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Contingency Table"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = ContingencyStudyConfig
        self.config: ContingencyStudyConfig = config

        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("contingency.description")
            + HTML.hr()
            + HTML.div(_ASSUMPTIONS_FINE_PRINT_EN, font_size=Style.FontSize.smaller)
        )
