#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class ReliabilityStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    correlation_type = attrs.field(default=None)
    scale_name = attrs.field(default=None)
    verbal_indicators = attrs.field(default=None)


# Fine-print on the exact methodology / variants this module uses. English only by
# design (only reports/tables are localised), rendered in a smaller font under the
# general description so the chosen conventions are explicit and auditable.
_ASSUMPTIONS_FINE_PRINT_EN = (
    "<b>Methodology &amp; assumptions</b>"
    "<ul>"
    "<li><b>Coefficient.</b> Cronbach&rsquo;s &alpha; computed from the item correlation "
    "matrix (standardised &alpha;): &alpha; = k/(k&minus;1) &middot; (1 &minus; tr(R)/&Sigma;R), "
    "where k is the number of items and R the item correlation matrix.</li>"
    "<li><b>Correlation type.</b> The same estimators as the Correlation analysis. Pearson, "
    "Spearman, Kendall&rsquo;s &tau;-b and Kendall&rsquo;s &tau;-c work on the items directly; "
    "Polychoric assumes an underlying continuous variable behind each ordinal item. Phi and "
    "Tetrachoric require binary items (&le; 2 unique values) and are rescaled to 0&ndash;1 "
    "first; Tetrachoric assumes an underlying continuous variable. (For ordinal Likert-type "
    "items, Polychoric is generally preferred over Pearson.)</li>"
    "<li><b>If item removed.</b> Each item&rsquo;s &lsquo;&alpha; if removed&rsquo; is &alpha; "
    "recomputed on the remaining items. The corrected item&ndash;total (item&ndash;rest) "
    "correlation is computed from the same item correlation matrix as &alpha; &mdash; "
    "r<sub>i</sub> = (&Sigma; of the item&rsquo;s off-diagonal correlations) / "
    "&radic;(variance of the rest-sum) with standardised items &mdash; rather than from the "
    "raw scores, so it stays consistent with the chosen correlation type (this is what "
    "psych::alpha reports when given a correlation matrix, and is the correct form for "
    "Phi / Tetrachoric / Polychoric). An item whose removal raises &alpha; may be weakening "
    "the scale.</li>"
    "<li><b>Interpretation.</b> &alpha; &gt; .9 excellent, &gt; .8 good, &gt; .7 acceptable, "
    "&gt; .6 questionable, &gt; .5 poor, otherwise unacceptable. &alpha; reflects only the "
    "correlation among items, not whether they belong together in content &mdash; that "
    "remains the researcher&rsquo;s judgement.</li>"
    "<li><b>Verbal indicators.</b> &lsquo;Verbal indicators in tables&rsquo; adds plain-language "
    "columns: the interpretation band next to &alpha;, and an &lsquo;Improves &alpha;?&rsquo; "
    "yes/no on the item table (yes = removing that item would raise &alpha;).</li>"
    "<li><b>Missing data.</b> Correlations are computed pairwise on the available values.</li>"
    "</ul>"
)


class ReliabilityResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ReliabilityStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Reliability"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = ReliabilityStudyConfig
        self.config: ReliabilityStudyConfig = config

        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("reliability.description")
            + HTML.hr()
            + HTML.div(_ASSUMPTIONS_FINE_PRINT_EN, font_size=Style.FontSize.smaller)
        )
