#  Copyright (c) 2023 StatPrism Team. All rights reserved.


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
