#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum


class PairedMethod(Enum):
    AUTO = "Detect automatically"
    PARAMETRIC = "Parametric (paired t / RM-ANOVA)"
    NON_PARAMETRIC = "Non-parametric (Wilcoxon / Friedman)"

    @staticmethod
    def get_values():
        return [e.value for e in PairedMethod]


class PairedAssumptionChecks(Enum):
    AUTO = "Auto"
    ALWAYS = "Yes"
    NEVER = "No"

    @staticmethod
    def get_values():
        return [e.value for e in PairedAssumptionChecks]
