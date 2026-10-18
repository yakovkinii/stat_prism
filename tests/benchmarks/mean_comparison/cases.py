from __future__ import annotations

import pandas as pd


def two_group_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "g": ["A"] * 6 + ["B"] * 6,
            "y": [10, 12, 11, 13, 9, 14, 15, 18, 16, 20, 14, 19],
        }
    )


def three_group_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "g": ["A"] * 5 + ["B"] * 5 + ["C"] * 5,
            "y": [10, 12, 11, 13, 9, 15, 18, 16, 20, 14, 8, 7, 9, 6, 10],
        }
    )


# Each case forces one test via the Method setting (so the benchmark covers every test branch) and
# names the supplement `kind` to read from the driven recalculate_mean_comparison_study. The two
# assumption-check studies force a parametric method with checks on ("always"), which emits the
# Shapiro and Levene tables alongside.
CASES = [
    {
        "study": "ttest_homogeneous",
        "data": two_group_data,
        "method": "homogeneous",
        "assumption": "never",
        "kind": "ttest_homogeneous",
    },
    {
        "study": "ttest_welch",
        "data": two_group_data,
        "method": "inhomogeneous",
        "assumption": "never",
        "kind": "ttest_welch",
    },
    {
        "study": "mann_whitney",
        "data": two_group_data,
        "method": "nonparametric",
        "assumption": "never",
        "kind": "mann_whitney",
    },
    {
        "study": "anova_oneway",
        "data": three_group_data,
        "method": "homogeneous",
        "assumption": "never",
        "kind": "anova_oneway",
    },
    {
        "study": "anova_welch",
        "data": three_group_data,
        "method": "inhomogeneous",
        "assumption": "never",
        "kind": "anova_welch",
    },
    {"study": "kruskal", "data": three_group_data, "method": "nonparametric", "assumption": "never", "kind": "kruskal"},
    {
        "study": "normality_shapiro",
        "data": two_group_data,
        "method": "homogeneous",
        "assumption": "always",
        "kind": "normality_check",
    },
    {
        "study": "homogeneity_levene",
        "data": two_group_data,
        "method": "homogeneous",
        "assumption": "always",
        "kind": "homogeneity_check",
    },
    # Post-hoc tables appear when the omnibus test is significant (the 3-group data is), with effect
    # size on. Each forced method produces its post-hoc: one-way -> Tukey, Welch -> Tamhane T2,
    # Kruskal -> Dunn.
    {
        "study": "posthoc_tukey",
        "data": three_group_data,
        "method": "homogeneous",
        "assumption": "never",
        "kind": "posthoc_tukey",
    },
    {
        "study": "posthoc_tamhane",
        "data": three_group_data,
        "method": "inhomogeneous",
        "assumption": "never",
        "kind": "posthoc_tamhane",
    },
    {
        "study": "posthoc_dunn",
        "data": three_group_data,
        "method": "nonparametric",
        "assumption": "never",
        "kind": "posthoc_dunn",
    },
]
