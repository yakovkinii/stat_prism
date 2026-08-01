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

# VALIDATED

from src.common.translations import t


def significance_verbal(p) -> str:
    """Significant / not significant at alpha = .05 (difference & association tests)."""
    return t("verbal.significant") if (p is not None and p < 0.05) else t("verbal.not_significant")


def assumption_met_verbal(p) -> str:
    """Yes / No for assumption checks where p > .05 means the assumption holds (e.g.
    normality, homogeneity of variance)."""
    return t("verbal.yes") if (p is not None and p > 0.05) else t("verbal.no")
