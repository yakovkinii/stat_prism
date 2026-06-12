#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum

import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


class RotationType(Enum):
    NONE = "none"
    VARIMAX = "varimax"
    PROMAX = "promax (obl)"
    OBLIMIN = "oblimin (obl)"
    OBLIMAX = "oblimax"
    QUARTIMIN = "quartimin (obl)"
    QUARTIMAX = "quartimax"
    EQUAMAX = "equamax"

    @staticmethod
    def get_values():
        return [e.value for e in RotationType]


class ExtractionMethod(Enum):
    MINRES = "Minimum Residual (MINRES)"
    ML = "Maximum Likelihood (ML)"
    PRINCIPAL = "Principal Axis (PAF)"

    @staticmethod
    def get_values():
        return [e.value for e in ExtractionMethod]


@attrs.define
class FactorAnalysisStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    method = attrs.field(default=None)
    rotation = attrs.field(default=None)
    n_factors = attrs.field(default=None)
    kaiser_normalization = attrs.field(default=None)
    plots = attrs.field(default=None)


# Fine-print on the exact methodology / variants this module uses. English only by
# design (only reports/tables are localised), rendered in a smaller font under the
# general description so the chosen conventions are explicit and auditable.
_ASSUMPTIONS_FINE_PRINT_EN = (
    "<b>Methodology &amp; assumptions</b>"
    "<ul>"
    "<li><b>Estimation.</b> Common-factor model fitted with factor_analyzer on the variable "
    "correlation matrix (squared multiple correlations as initial communalities). Extraction: "
    "MINRES, Maximum Likelihood, or Principal Axis. Rows with any missing value are dropped "
    "(list-wise) and ordinal items are scored numerically.</li>"
    "<li><b>Sampling adequacy.</b> The Kaiser&ndash;Meyer&ndash;Olkin (KMO) measure (overall "
    "and per-variable MSA) and Bartlett&rsquo;s test of sphericity gauge whether the "
    "correlations support factoring (KMO &gt; .6 and a significant Bartlett test are usually "
    "wanted).</li>"
    "<li><b>Eigenvalues.</b> Eigenvalues of the correlation matrix with the percentage and "
    "cumulative percentage of variance; the scree plot and the Kaiser criterion "
    "(eigenvalue &gt; 1) help choose the number of factors &mdash; a guide, not a rule.</li>"
    "<li><b>Rotation.</b> Orthogonal (Varimax / Quartimax / Equamax / Oblimax) keeps factors "
    "uncorrelated; oblique (Promax / Oblimin / Quartimin) allows correlated factors and adds a "
    "factor-correlation matrix (&Phi;) and a structure matrix. Kaiser normalisation can be "
    "toggled.</li>"
    "<li><b>Loadings.</b> The loadings (pattern) matrix is the direct factor&rarr;variable "
    "effect &mdash; use it to assign variables to factors. Communality is the variance of a "
    "variable explained by the factors; uniqueness is 1 &minus; communality. The structure "
    "matrix (oblique only) is the variable&ndash;factor correlation including shared factor "
    "variance.</li>"
    "<li><b>Out-of-range loadings.</b> A <i>negative</i> loading is normal &mdash; it just means "
    "the variable relates inversely to the factor (a reverse-keyed item); interpret its "
    "magnitude as usual. A loading or communality <i>above 1</i> (equivalently a negative "
    "uniqueness) is a <b>Heywood case</b>: an improper solution. In an oblique <i>pattern</i> "
    "matrix a value slightly above 1 can occur legitimately when factors are strongly "
    "correlated (regression-like weights, not correlations), but a communality &gt; 1 is always "
    "invalid. It usually signals an over-extracted model (too many factors for the data), a "
    "small sample, or near-collinear / duplicate items. Typical fixes: extract fewer factors, "
    "remove redundant items, gather more data, or try a different extraction/rotation.</li>"
    "</ul>"
)


class FactorAnalysisResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: FactorAnalysisStudyConfig):
        super().__init__(unique_id)
        self.title = "Exploratory Factor Analysis"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = FactorAnalysisStudyConfig
        self.config: FactorAnalysisStudyConfig = config
        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("efa.description")
            + HTML.hr()
            + HTML.div(_ASSUMPTIONS_FINE_PRINT_EN, font_size=Style.FontSize.smaller)
        )
