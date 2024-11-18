#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#
from enum import Enum

DESCRIPTION = """
<h2> Contingency Table and Chi squared test</h2>
"""


class MeanComparisonMethod(Enum):
    AUTO = "Detect automatically"
    HOMOGENEOUS = "Parametric homogeneous (t-test/ANOVA)"
    INHOMOGENEOUS = "Parametric inhomogeneous (Welch's)"
    NON_PARAMETRIC = "Non-parametric (Mann-Whitney/Kruskal-Wallis)"

    @staticmethod
    def get_values():
        return [e.value for e in MeanComparisonMethod]
