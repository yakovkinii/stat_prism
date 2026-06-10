#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.stats import kendalltau, pearsonr, spearmanr
from scipy.stats import norm, multivariate_normal, chi2

from src.side_area_panel.modules.common.mathematics.correlation.binary_correlations import (
    phi_coefficient,
    tetrachoric_corr_2x2_table,
)
from src.side_area_panel.modules.correlation.result import CorrelationType


def polychoric_corr_with_pvalue(x, y, min_prob=1e-12):
    """
    Polychoric correlation with likelihood-ratio-test p-value.

    H0: latent correlation rho = 0

    Returns
    -------
    corr : float
        Estimated polychoric correlation.
    p_value : float
        Asymptotic likelihood-ratio p-value.
    """

    data = pd.DataFrame({"x": x, "y": y}).dropna()

    if len(data) < 4:
        return np.nan, np.nan

    if data["x"].nunique() < 2 or data["y"].nunique() < 2:
        return np.nan, np.nan

    # Respect ordered categorical dtype if present.
    if isinstance(data["x"].dtype, pd.CategoricalDtype) and data["x"].cat.ordered:
        x_categories = list(data["x"].cat.categories)
    else:
        x_categories = sorted(data["x"].unique())

    if isinstance(data["y"].dtype, pd.CategoricalDtype) and data["y"].cat.ordered:
        y_categories = list(data["y"].cat.categories)
    else:
        y_categories = sorted(data["y"].unique())

    table = pd.crosstab(
        pd.Categorical(data["x"], categories=x_categories, ordered=True),
        pd.Categorical(data["y"], categories=y_categories, ordered=True),
        dropna=False,
    ).to_numpy(dtype=float)

    n = table.sum()

    if n < 4:
        return np.nan, np.nan

    row_props = table.sum(axis=1) / n
    col_props = table.sum(axis=0) / n

    row_cum = np.cumsum(row_props)[:-1]
    col_cum = np.cumsum(col_props)[:-1]

    row_cum = np.clip(row_cum, min_prob, 1 - min_prob)
    col_cum = np.clip(col_cum, min_prob, 1 - min_prob)

    row_thresholds = np.concatenate(
        [[-np.inf], norm.ppf(row_cum), [np.inf]]
    )
    col_thresholds = np.concatenate(
        [[-np.inf], norm.ppf(col_cum), [np.inf]]
    )

    def bvncdf(a, b, rho):
        if np.isneginf(a) or np.isneginf(b):
            return 0.0

        if np.isposinf(a) and np.isposinf(b):
            return 1.0

        if np.isposinf(a):
            return norm.cdf(b)

        if np.isposinf(b):
            return norm.cdf(a)

        return multivariate_normal.cdf(
            [a, b],
            mean=[0.0, 0.0],
            cov=[[1.0, rho], [rho, 1.0]],
        )

    def cell_prob(i, j, rho):
        lx = row_thresholds[i]
        ux = row_thresholds[i + 1]
        ly = col_thresholds[j]
        uy = col_thresholds[j + 1]

        p = (
            bvncdf(ux, uy, rho)
            - bvncdf(lx, uy, rho)
            - bvncdf(ux, ly, rho)
            + bvncdf(lx, ly, rho)
        )

        return max(float(p), min_prob)

    def log_likelihood(rho):
        ll = 0.0

        for i in range(table.shape[0]):
            for j in range(table.shape[1]):
                count = table[i, j]

                if count > 0:
                    ll += count * np.log(cell_prob(i, j, rho))

        return ll

    result = minimize_scalar(
        lambda rho: -log_likelihood(rho),
        bounds=(-0.999, 0.999),
        method="bounded",
        options={"xatol": 1e-6},
    )

    if not result.success:
        return np.nan, np.nan

    corr = float(result.x)

    ll_fitted = log_likelihood(corr)
    ll_null = log_likelihood(0.0)

    lr_stat = 2.0 * (ll_fitted - ll_null)
    lr_stat = max(lr_stat, 0.0)

    p_value = chi2.sf(lr_stat, df=1)

    return corr, p_value

def calculate_correlations(df, kind: CorrelationType):
    correlation_matrix = pd.DataFrame(index=df.columns, columns=df.columns)
    p_matrix = pd.DataFrame(index=df.columns, columns=df.columns)
    df_matrix = pd.DataFrame(index=df.columns, columns=df.columns)

    # Calculate correlation, p-values, and degrees of freedom for each pair of columns
    for i1, col1 in enumerate(df.columns):
        for i2, col2 in enumerate(df.columns):
            if i1 <= i2:
                continue
            # Drop NA values for the pair of columns
            valid_data = df[[col1, col2]].dropna()

            if kind == CorrelationType.PEARSON:
                # Compute correlation and p-value
                corr, p_value = pearsonr(valid_data[col1], valid_data[col2])
                degrees_of_freedom = len(valid_data) - 2
            elif kind == CorrelationType.SPEARMAN:
                corr, p_value = spearmanr(valid_data[col1], valid_data[col2])
                degrees_of_freedom = np.nan  # Not available
            elif kind == CorrelationType.KENDALL:
                corr, p_value = kendalltau(valid_data[col1], valid_data[col2])
                degrees_of_freedom = np.nan  # Not available
            elif kind == CorrelationType.KENDALL_C:
                corr, p_value = kendalltau(valid_data[col1], valid_data[col2], variant='c')
                degrees_of_freedom = np.nan  # Not available
            elif kind == CorrelationType.POLYCHORIC:
                corr, p_value = polychoric_corr_with_pvalue(
                    valid_data[col1],
                    valid_data[col2],
                )
                degrees_of_freedom = np.nan  # Not available
            elif kind == CorrelationType.PHI:
                corr, p_value, degrees_of_freedom = phi_coefficient(valid_data[col1], valid_data[col2])
            elif kind == CorrelationType.TETRACHORIC:
                # Tetrachoric is defined for 2x2 tables of the current pair; return blank
                # otherwise instead of crashing.
                table = pd.crosstab(valid_data[col1], valid_data[col2]).values
                if table.shape == (2, 2):
                    corr, _, p_value, degrees_of_freedom = tetrachoric_corr_2x2_table(table=table)
                else:
                    corr, p_value, degrees_of_freedom = np.nan, np.nan, np.nan
            else:
                raise ValueError(f"Invalid correlation type: {kind}")

            # Fill the square matrix
            correlation_matrix.loc[col1, col2] = corr
            p_matrix.loc[col1, col2] = p_value
            df_matrix.loc[col1, col2] = degrees_of_freedom

    return correlation_matrix, p_matrix, df_matrix
