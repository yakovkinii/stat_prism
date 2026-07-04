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


from enum import Enum


class MeanComparisonMethod(Enum):
    AUTO = "Detect automatically"
    HOMOGENEOUS = "Parametric homogeneous (t-test/ANOVA)"
    INHOMOGENEOUS = "Parametric inhomogeneous (Welch's)"
    NON_PARAMETRIC = "Non-parametric (Mann-Whitney/Kruskal-Wallis)"

    @staticmethod
    def get_values():
        return [e.value for e in MeanComparisonMethod]


class MissingValuesInGrouping(Enum):
    SKIP = "Skip missing"
    TREAT_AS_NA = 'Treat as "N/A"'

    @staticmethod
    def get_values():
        return [e.value for e in MissingValuesInGrouping]


class AssumptionChecksInGrouping(Enum):
    AUTO = "Auto"
    ALWAYS = "Yes"
    NEVER = "No"

    @staticmethod
    def get_values():
        return [e.value for e in AssumptionChecksInGrouping]
