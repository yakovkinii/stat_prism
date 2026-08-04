#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.


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
