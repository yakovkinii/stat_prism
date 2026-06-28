#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import numpy as np
import pandas as pd
import pingouin as pg
from scipy.optimize import minimize_scalar
from scipy.stats import chi2, kendalltau, multivariate_normal, norm, pearsonr, spearmanr

from src.side_area_panel.modules.common.mathematics.correlation.binary_correlations import (
    phi_coefficient,
    tetrachoric_corr_2x2_table,
)
from src.side_area_panel.modules.correlation.correlation_result import CorrelationType


def calculate_partial_correlations(df, variables, controls, kind: CorrelationType):
    """Partial correlation matrix among `variables`, controlling for `controls`. Returns
    (correlation_matrix, p_matrix, df_matrix) with the same lower-triangle layout as
    calculate_correlations. Only Pearson and Spearman are supported (the caller validates)."""
    method = "spearman" if kind == CorrelationType.SPEARMAN else "pearson"
    controls = [c for c in controls if c not in variables]  # a control can't be a target

    correlation_matrix = pd.DataFrame(index=variables, columns=variables)
    p_matrix = pd.DataFrame(index=variables, columns=variables)
    df_matrix = pd.DataFrame(index=variables, columns=variables)

    for i1, col1 in enumerate(variables):
        for i2, col2 in enumerate(variables):
            if i1 <= i2:
                continue
            valid = df[[col1, col2] + controls].dropna()
            n = len(valid)
            if n <= len(controls) + 2:
                corr, p_value, dof = np.nan, np.nan, np.nan
            else:
                res = pg.partial_corr(data=valid, x=col1, y=col2, covar=controls, method=method)
                corr = float(res["r"].iloc[0])
                p_value = float(res["p-val"].iloc[0])
                # Pearson and Spearman both carry df = n - 2 - #controls (Spearman needs it
                # for the Fisher-z CI); other coefficients have no df.
                dof = (n - 2 - len(controls)) if kind in (CorrelationType.PEARSON, CorrelationType.SPEARMAN) else np.nan

            correlation_matrix.loc[col1, col2] = corr
            p_matrix.loc[col1, col2] = p_value
            df_matrix.loc[col1, col2] = dof

    return correlation_matrix, p_matrix, df_matrix


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

    row_thresholds = np.concatenate([[-np.inf], norm.ppf(row_cum), [np.inf]])
    col_thresholds = np.concatenate([[-np.inf], norm.ppf(col_cum), [np.inf]])

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

        p = bvncdf(ux, uy, rho) - bvncdf(lx, uy, rho) - bvncdf(ux, ly, rho) + bvncdf(lx, ly, rho)

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


def _pair_correlation(series1, series2, kind: CorrelationType):
    """Correlation, p-value and degrees of freedom for one pair of series (pairwise
    deletion). Shared by the square and cross (two-set) matrices."""
    valid = pd.concat([series1, series2], axis=1).dropna()
    a = valid.iloc[:, 0]
    b = valid.iloc[:, 1]

    if kind == CorrelationType.PEARSON:
        corr, p_value = pearsonr(a, b)
        degrees_of_freedom = len(valid) - 2
    elif kind == CorrelationType.SPEARMAN:
        corr, p_value = spearmanr(a, b)
        # df = n - 2 (scipy's Spearman p-value uses the same t-approximation); also the
        # n carrier the Fisher-z confidence interval needs.
        degrees_of_freedom = len(valid) - 2
    elif kind == CorrelationType.KENDALL:
        corr, p_value = kendalltau(a, b)
        degrees_of_freedom = np.nan  # Not available
    elif kind == CorrelationType.KENDALL_C:
        corr, p_value = kendalltau(a, b, variant="c")
        degrees_of_freedom = np.nan  # Not available
    elif kind == CorrelationType.POLYCHORIC:
        corr, p_value = polychoric_corr_with_pvalue(a, b)
        degrees_of_freedom = np.nan  # Not available
    elif kind == CorrelationType.PHI:
        corr, p_value, degrees_of_freedom = phi_coefficient(a, b)
    elif kind == CorrelationType.TETRACHORIC:
        # Tetrachoric is defined for 2x2 tables of the current pair; return blank
        # otherwise instead of crashing.
        table = pd.crosstab(a, b).values
        if table.shape == (2, 2):
            corr, _, p_value, degrees_of_freedom = tetrachoric_corr_2x2_table(table=table)
        else:
            corr, p_value, degrees_of_freedom = np.nan, np.nan, np.nan
    else:
        raise ValueError(f"Invalid correlation type: {kind}")

    return corr, p_value, degrees_of_freedom


def calculate_correlations(df, kind: CorrelationType):
    correlation_matrix = pd.DataFrame(index=df.columns, columns=df.columns)
    p_matrix = pd.DataFrame(index=df.columns, columns=df.columns)
    df_matrix = pd.DataFrame(index=df.columns, columns=df.columns)

    # Calculate correlation, p-values, and degrees of freedom for each pair of columns
    for i1, col1 in enumerate(df.columns):
        for i2, col2 in enumerate(df.columns):
            if i1 <= i2:
                continue
            corr, p_value, degrees_of_freedom = _pair_correlation(df[col1], df[col2], kind)

            # Fill the square matrix
            correlation_matrix.loc[col1, col2] = corr
            p_matrix.loc[col1, col2] = p_value
            df_matrix.loc[col1, col2] = degrees_of_freedom

    return correlation_matrix, p_matrix, df_matrix


def calculate_cross_correlations(df, rows, cols, kind: CorrelationType):
    """Rectangular correlation matrix between two variable sets: every (row, col) pair is
    computed (full grid), index = `rows`, columns = `cols`."""
    correlation_matrix = pd.DataFrame(index=rows, columns=cols)
    p_matrix = pd.DataFrame(index=rows, columns=cols)
    df_matrix = pd.DataFrame(index=rows, columns=cols)

    for row in rows:
        for col in cols:
            corr, p_value, degrees_of_freedom = _pair_correlation(df[row], df[col], kind)
            correlation_matrix.loc[row, col] = corr
            p_matrix.loc[row, col] = p_value
            df_matrix.loc[row, col] = degrees_of_freedom

    return correlation_matrix, p_matrix, df_matrix


def calculate_partial_cross_correlations(df, rows, cols, controls, kind: CorrelationType):
    """Rectangular partial correlation matrix between two variable sets, controlling for
    `controls`. Pearson and Spearman only (the caller validates). A control that coincides
    with a row/col is dropped from the covariate set for that pair."""
    method = "spearman" if kind == CorrelationType.SPEARMAN else "pearson"

    correlation_matrix = pd.DataFrame(index=rows, columns=cols)
    p_matrix = pd.DataFrame(index=rows, columns=cols)
    df_matrix = pd.DataFrame(index=rows, columns=cols)

    for row in rows:
        for col in cols:
            if row == col:
                correlation_matrix.loc[row, col] = 1.0
                p_matrix.loc[row, col] = 0.0
                df_matrix.loc[row, col] = np.nan
                continue
            pair_controls = [c for c in controls if c not in (row, col)]
            valid = df[[row, col] + pair_controls].dropna()
            n = len(valid)
            if n <= len(pair_controls) + 2:
                corr, p_value, dof = np.nan, np.nan, np.nan
            else:
                res = pg.partial_corr(data=valid, x=row, y=col, covar=pair_controls, method=method)
                corr = float(res["r"].iloc[0])
                p_value = float(res["p-val"].iloc[0])
                dof = (
                    (n - 2 - len(pair_controls))
                    if kind in (CorrelationType.PEARSON, CorrelationType.SPEARMAN)
                    else np.nan
                )

            correlation_matrix.loc[row, col] = corr
            p_matrix.loc[row, col] = p_value
            df_matrix.loc[row, col] = dof

    return correlation_matrix, p_matrix, df_matrix
