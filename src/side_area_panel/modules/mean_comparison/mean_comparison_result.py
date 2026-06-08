#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class MeanComparisonStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    method = attrs.field(default=None)
    grouping_missing = attrs.field(default=None)
    assumption_checks = attrs.field(default=None)
    effect_size = attrs.field(default=None)
    plots = attrs.field(default=None)


# Fine-print on the exact methodology / variants this module uses. English only by
# design (only reports/tables are localised), rendered in a smaller font under the
# general description so the chosen conventions are explicit and auditable.
_ASSUMPTIONS_FINE_PRINT_EN = (
    "<b>Methodology &amp; assumptions</b>"
    "<ul>"
    "<li><b>Test selection.</b> Two groups use the t-test family; three or more use the "
    "ANOVA family. Numeric variables that pass the assumption checks use parametric tests; "
    "ordinal / non-numeric variables and numeric variables that fail normality use "
    "non-parametric tests.</li>"
    "<li><b>Normality.</b> Shapiro&ndash;Wilk, computed per group. A variable is treated as "
    "normal only when every group passes (p &gt; .05).</li>"
    "<li><b>Homogeneity of variance.</b> Levene&rsquo;s test centred on the <i>mean</i> "
    "(not the median / Brown&ndash;Forsythe variant). Equal variances are assumed when "
    "p &gt; .05.</li>"
    "<li><b>Parametric, 2 groups.</b> Equal variances &rarr; Student&rsquo;s independent "
    "t-test (pooled SD); unequal variances &rarr; Welch&rsquo;s t-test with "
    "Welch&ndash;Satterthwaite degrees of freedom.</li>"
    "<li><b>Parametric, 3+ groups.</b> Equal variances &rarr; one-way ANOVA; unequal "
    "variances &rarr; Welch&rsquo;s ANOVA.</li>"
    "<li><b>Non-parametric.</b> Two groups &rarr; Mann&ndash;Whitney U; three or more "
    "&rarr; Kruskal&ndash;Wallis H.</li>"
    "<li><b>Effect sizes.</b>"
    "<ul>"
    "<li>Student&rsquo;s t: Cohen&rsquo;s d using the pooled SD.</li>"
    "<li>Welch&rsquo;s t: Cohen&rsquo;s d standardised by the root-mean of the two group "
    "variances, &radic;((s<sub>1</sub><sup>2</sup>+s<sub>2</sub><sup>2</sup>)/2), rather "
    "than the pooled SD.</li>"
    "<li>Mann&ndash;Whitney: rank-biserial correlation "
    "r = 1 &minus; 2&middot;U<sub>1</sub>/(n<sub>1</sub>&middot;n<sub>2</sub>), reported "
    "<i>with its sign</i> so the direction of the effect is preserved; the U printed in the "
    "table is the smaller of U<sub>1</sub>/U<sub>2</sub>.</li>"
    "<li>The ANOVA family reports no effect-size statistic &mdash; the "
    "&ldquo;Effect size / Post-hoc&rdquo; switch controls only the post-hoc tests.</li>"
    "</ul></li>"
    "<li><b>Post-hoc</b> (only when enabled and the omnibus test is significant): one-way "
    "ANOVA &rarr; Tukey HSD; Welch&rsquo;s ANOVA &rarr; Tamhane&rsquo;s T2; "
    "Kruskal&ndash;Wallis &rarr; Dunn&rsquo;s test.</li>"
    "<li><b>Threshold.</b> All tests are two-sided and use &alpha; = .05.</li>"
    "<li><b>Missing data.</b> Missing values are dropped per variable before each test; "
    "missing group labels follow the &ldquo;Missing in grouping&rdquo; setting.</li>"
    "</ul>"
)


class MeanComparisonResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: MeanComparisonStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "T-test/ANOVA"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = MeanComparisonStudyConfig
        self.config: MeanComparisonStudyConfig = config

        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("ttest.description")
            + HTML.hr()
            + HTML.div(_ASSUMPTIONS_FINE_PRINT_EN, font_size=Style.FontSize.smaller)
        )
