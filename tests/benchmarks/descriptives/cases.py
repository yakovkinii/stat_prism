from __future__ import annotations

import pandas as pd


def numeric_data() -> pd.DataFrame:
    # Includes two missing values to exercise the N / missing counts and pairwise dropna.
    return pd.DataFrame(
        {
            "x": [12, 15, 14, 10, 18, 20, 13, 16, 11, 19, 17, 14, 15, 13, 21, 9, 16, 18, 12, 17, None, None],
        }
    )


def skewed_data() -> pd.DataFrame:
    # Clearly non-normal (right-skewed) so the normality tests land in their meaningful range, where
    # every implementation's p-value approximation agrees (the upper tail is where they saturate).
    return pd.DataFrame(
        {
            "x": [1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 5, 7, 9, 12, 18, 25, 2, 1, 3, 6],
        }
    )


# Each case drives one of the two Qt-free compute functions in descriptive_main:
#   * summary   -> _numeric_stats (N, missing, mean, SD, SE, median, Q1, Q3, skewness, kurtosis, min, max)
#   * normality -> _normality_stats for one of the three selectable tests.
CASES = [
    {"study": "numeric_summary", "data": numeric_data, "mode": "summary", "column": "x"},
    {"study": "normality_shapiro", "data": skewed_data, "mode": "normality", "column": "x", "test": "Shapiro-Wilk"},
    {
        "study": "normality_lilliefors",
        "data": skewed_data,
        "mode": "normality",
        "column": "x",
        "test": "Kolmogorov-Smirnov",
    },
    {
        "study": "normality_anderson_darling",
        "data": skewed_data,
        "mode": "normality",
        "column": "x",
        "test": "Anderson-Darling",
    },
]
