#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Verbal (plain-language) interpretation of effect-size magnitudes, shared by the
modules that show a 'verbal indicators' effect-size column. Thresholds follow the usual
conventions; the returned strings are localised."""


from src.common.translations import t


def cohen_d_magnitude(d) -> str:
    """Cohen's d magnitude: |d| < 0.2 negligible, < 0.5 small, < 0.8 medium, else large."""
    magnitude = abs(d)
    if magnitude < 0.2:
        key = "negligible"
    elif magnitude < 0.5:
        key = "small"
    elif magnitude < 0.8:
        key = "medium"
    else:
        key = "large"
    return t(f"effect.magnitude.{key}")


def correlation_magnitude(r) -> str:
    """Correlation-type magnitude (e.g. rank-biserial), reusing the correlation module's
    strength bands: |r| > .5 strong, > .3 moderate, > .1 weak, otherwise very weak."""
    magnitude = abs(r)
    if magnitude > 0.5:
        return t("correlation.strength.strong")
    if magnitude > 0.3:
        return t("correlation.strength.moderate")
    if magnitude > 0.1:
        return t("correlation.strength.weak")
    return t("correlation.strength.very_weak")
