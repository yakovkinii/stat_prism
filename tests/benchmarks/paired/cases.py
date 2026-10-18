from __future__ import annotations

import pandas as pd

# Two within-subject conditions (pre/post). Numeric so the parametric and non-parametric families
# both run on the same values (ordinal vs numeric is out of scope for these benchmarks). The pre-post
# differences are all non-zero with distinct absolute values (no ties), so scipy's exact Wilcoxon p
# equals R's exact p -- with ties R falls back to the normal approximation and the two diverge.
PRE = [20, 22, 21, 23, 19, 24, 18, 25, 20, 22]
POST = [23, 20, 26, 19, 25, 25, 10, 32, 11, 32]

# Three within-subject conditions (repeated measures). The middle condition is elevated with varied
# gaps so the omnibus tests are significant, the post-hoc tables appear, and no pairwise difference is
# constant (a constant difference would make the paired t-test undefined).
T1 = [10, 12, 11, 13, 9, 14, 8, 15, 10, 12]
T2 = [13, 16, 14, 18, 11, 16, 12, 20, 12, 17]
T3 = [11, 10, 12, 9, 13, 10, 14, 11, 12, 10]


def two_condition_data() -> pd.DataFrame:
    return pd.DataFrame({"pre": PRE, "post": POST})


def three_condition_data() -> pd.DataFrame:
    return pd.DataFrame({"t1": T1, "t2": T2, "t3": T3})


# Each case forces one family via the Method setting and names the supplement `kind` to read from the
# driven recalculate_paired_study. Assumption-check studies force the parametric family with checks on
# ("always") so the Shapiro / sphericity table is emitted on numeric values.
CASES = [
    {
        "study": "paired_t",
        "data": two_condition_data,
        "conditions": ["pre", "post"],
        "method": "parametric",
        "assumption": "never",
        "kind": "paired_t",
    },
    {
        "study": "wilcoxon",
        "data": two_condition_data,
        "conditions": ["pre", "post"],
        "method": "nonparametric",
        "assumption": "never",
        "kind": "wilcoxon",
    },
    {
        "study": "rm_anova",
        "data": three_condition_data,
        "conditions": ["t1", "t2", "t3"],
        "method": "parametric",
        "assumption": "never",
        "kind": "rm_anova",
    },
    {
        "study": "friedman",
        "data": three_condition_data,
        "conditions": ["t1", "t2", "t3"],
        "method": "nonparametric",
        "assumption": "never",
        "kind": "friedman",
    },
    {
        "study": "descriptives_two",
        "data": two_condition_data,
        "conditions": ["pre", "post"],
        "method": "parametric",
        "assumption": "never",
        "kind": "paired_descriptives",
    },
    {
        "study": "descriptives_three",
        "data": three_condition_data,
        "conditions": ["t1", "t2", "t3"],
        "method": "parametric",
        "assumption": "never",
        "kind": "paired_descriptives",
    },
    {
        "study": "normality_two",
        "data": two_condition_data,
        "conditions": ["pre", "post"],
        "method": "parametric",
        "assumption": "always",
        "kind": "paired_normality",
    },
    {
        "study": "normality_three",
        "data": three_condition_data,
        "conditions": ["t1", "t2", "t3"],
        "method": "parametric",
        "assumption": "always",
        "kind": "paired_normality",
    },
    {
        "study": "posthoc_param",
        "data": three_condition_data,
        "conditions": ["t1", "t2", "t3"],
        "method": "parametric",
        "assumption": "never",
        "kind": "paired_posthoc_param",
    },
    {
        "study": "posthoc_nonparam",
        "data": three_condition_data,
        "conditions": ["t1", "t2", "t3"],
        "method": "nonparametric",
        "assumption": "never",
        "kind": "paired_posthoc_nonparam",
    },
]
