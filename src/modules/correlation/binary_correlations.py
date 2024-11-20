#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import chi2_contingency, multivariate_normal, norm


# Calculate Phi Correlation using contingency tables
def phi_coefficient(var1, var2):
    contingency_table = pd.crosstab(var1, var2)
    chi2, p_value, dof, _ = chi2_contingency(contingency_table)
    n = contingency_table.sum().sum()
    phi = np.sqrt(chi2 / n)
    return phi, p_value, dof


# Calculate Phi Correlation Table
def phi_correlation_table(df):
    cols = df.columns
    corr_matrix = pd.DataFrame(np.zeros((len(cols), len(cols))), index=cols, columns=cols)

    for i in range(len(cols)):
        for j in range(i, len(cols)):
            corr, _, _ = phi_coefficient(df[cols[i]], df[cols[j]])
            corr_matrix.iloc[i, j] = corr
            corr_matrix.iloc[j, i] = corr
    return corr_matrix


def tetrachoric_corr_2x2_table(table):
    """
    Estimate tetrachoric correlation from a 2x2 contingency table.
    Returns:
        rho_est: Estimated tetrachoric correlation
        se: Standard error of the estimate
        p_value: Two-tailed p-value
        df: Degrees of freedom
    """
    assert table.shape == (2, 2), "Input must be a 2x2 table"

    # Proportions in each cell
    a, b = table[0, 0], table[0, 1]
    c, d = table[1, 0], table[1, 1]
    n = a + b + c + d

    # Marginal proportions with epsilon to prevent 0 or 1
    epsilon = 1e-6
    p1 = (a + b) / n
    p2 = (a + c) / n
    p1 = np.clip(p1, epsilon, 1 - epsilon)
    p2 = np.clip(p2, epsilon, 1 - epsilon)

    # Function to compute the negative log likelihood
    def neg_log_likelihood(rho):
        rho = rho.item()  # Extract scalar from array

        # Inverse of CDF of the marginal proportions (used as thresholds)
        phi_a = norm.ppf(p1)
        phi_b = norm.ppf(p2)

        # Define the covariance matrix for the bivariate normal distribution
        cov_matrix = np.array([[1, rho], [rho, 1]])

        # Compute probabilities for each quadrant of the 2x2 table
        try:
            prob_11 = multivariate_normal.cdf([phi_a, phi_b], mean=[0, 0], cov=cov_matrix)
        except np.linalg.LinAlgError:
            return np.inf  # Return a large value if covariance matrix is not positive definite

        prob_10 = norm.cdf(phi_a) - prob_11
        prob_01 = norm.cdf(phi_b) - prob_11
        prob_00 = 1 - prob_11 - prob_10 - prob_01

        # Ensure all probabilities are positive and finite
        probs = [prob_11, prob_10, prob_01, prob_00]
        if any([p <= 0 or not np.isfinite(p) for p in probs]):
            return np.inf

        # Log likelihood
        return -(a * np.log(prob_11) + b * np.log(prob_10) + c * np.log(prob_01) + d * np.log(prob_00))

    # Adjust bounds to avoid singularities
    bounds = [(-1 + epsilon, 1 - epsilon)]
    result = minimize(neg_log_likelihood, x0=[0.0], bounds=bounds, method="L-BFGS-B")

    rho_est = result.x[0]  # Estimated correlation

    # Compute standard error
    se = (1 / np.sqrt(n)) * (1 / (1 - rho_est**2))

    # Compute z-score
    z = rho_est / se

    # Compute two-tailed p-value
    p_value = 2 * (1 - norm.cdf(abs(z)))

    # Degrees of freedom
    df = n - 2

    return rho_est, se, p_value, df


def tetrachoric_corr_matrix(df):
    cols = df.columns
    n_cols = len(cols)
    corr_matrix = pd.DataFrame(np.zeros((n_cols, n_cols)), index=cols, columns=cols)
    p_value_matrix = pd.DataFrame(np.zeros((n_cols, n_cols)), index=cols, columns=cols)
    se_matrix = pd.DataFrame(np.zeros((n_cols, n_cols)), index=cols, columns=cols)
    df_matrix = pd.DataFrame(np.zeros((n_cols, n_cols)), index=cols, columns=cols)

    for i in range(n_cols):
        for j in range(i, n_cols):
            # Create a 2x2 contingency table for the two variables
            table = pd.crosstab(df.iloc[:, i], df.iloc[:, j]).values
            if table.shape == (2, 2):
                rho_est, se, p_value, df_value = tetrachoric_corr_2x2_table(table)
                corr_matrix.iloc[i, j] = rho_est
                corr_matrix.iloc[j, i] = rho_est
                p_value_matrix.iloc[i, j] = p_value
                p_value_matrix.iloc[j, i] = p_value
                se_matrix.iloc[i, j] = se
                se_matrix.iloc[j, i] = se
                df_matrix.iloc[i, j] = df_value
                df_matrix.iloc[j, i] = df_value
            else:
                corr_matrix.iloc[i, j] = np.nan
                corr_matrix.iloc[j, i] = np.nan
                p_value_matrix.iloc[i, j] = np.nan
                p_value_matrix.iloc[j, i] = np.nan
                se_matrix.iloc[i, j] = np.nan
                se_matrix.iloc[j, i] = np.nan
                df_matrix.iloc[i, j] = np.nan
                df_matrix.iloc[j, i] = np.nan

    return corr_matrix, p_value_matrix, se_matrix, df_matrix
