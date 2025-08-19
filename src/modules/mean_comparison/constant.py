#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum

DESCRIPTION = """
<h2> Mean Comparison (Independent Samples)</h2>
<h3> Description </h3>
<div>
    Compare the means of two or more groups to determine if they are significantly different.
</div>
<div>
    If the grouping column has two unique values, the tests from t-test family are used:
    <ul>
    <li>If the variable is non-numerical, or if the data is not normally distributed (Shapiro-Wilk normality test),
    the Mann-Whitney U test is used.
    <li>If the homogeneity of variance assumption (Levene's homogeneity test) is violated, the Welch's t-test is used.
    <li>Otherwise, the independent samples t-test is used.
    </ul>
</div>
<div>
    If the grouping column has more than two unique values, the tests from ANOVA family are used:
    <ul>
    <li>If the variable is non-numerical, or if the data is not normally distributed (Shapiro-Wilk normality test),
    the Kruskal-Wallis test is used.
    <li>If the homogeneity of variance assumption (Levene's homogeneity test) is violated, Welch's ANOVA is used.
    <li>Otherwise, one-way ANOVA is used.
    </ul>
</div>
<h3> Inputs </h3>
<div>
    <b>Variable(s):</b><br>
    The variable(s) to compare.
</div>
<div>
    <b>Grouping Column:</b><br>
    The column that defines the groups to compare (such as respondent's sex or age group).
</div>
"""


class MeanComparisonMethod(Enum):
    AUTO = "Detect automatically"
    HOMOGENEOUS = "Parametric homogeneous (t-test/ANOVA)"
    INHOMOGENEOUS = "Parametric inhomogeneous (Welch's)"
    NON_PARAMETRIC = "Non-parametric (Mann-Whitney/Kruskal-Wallis)"

    @staticmethod
    def get_values():
        return [e.value for e in MeanComparisonMethod]
