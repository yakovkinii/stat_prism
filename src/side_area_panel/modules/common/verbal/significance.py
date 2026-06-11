#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Plain-language verbal indicators placed next to p-values when 'verbal indicators in
tables' is on. Significance for difference/association tests; a yes/no conclusion for
assumption checks (where p > .05 means the assumption holds)."""


from src.common.translations import t


def significance_verbal(p) -> str:
    """Significant / not significant at α = .05 (difference & association tests)."""
    return t("verbal.significant") if (p is not None and p < 0.05) else t("verbal.not_significant")


def assumption_met_verbal(p) -> str:
    """Yes / No for assumption checks where p > .05 means the assumption holds (e.g.
    normality, homogeneity of variance)."""
    return t("verbal.yes") if (p is not None and p > 0.05) else t("verbal.no")
