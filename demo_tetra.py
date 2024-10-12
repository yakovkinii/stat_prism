import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm
from scipy.stats import multivariate_normal


# Function to estimate the tetrachoric correlation
def tetrachoric_corr_2x2_table(table):
    """
    Estimate tetrachoric correlation from a 2x2 contingency table.
    """
    assert table.shape == (2, 2), "Input must be a 2x2 table"

    # Proportions in each cell
    a, b = table[0, 0], table[0, 1]
    c, d = table[1, 0], table[1, 1]
    n = a + b + c + d

    # Marginal proportions
    epsilon = 1e-6
    p1 = (a + b) / n
    p2 = (a + c) / n
    p1 = np.clip(p1, epsilon, 1 - epsilon)  # Ensure p1 is in (0,1)
    p2 = np.clip(p2, epsilon, 1 - epsilon)  # Ensure p2 is in (0,1)

    def neg_log_likelihood(rho):
        rho = rho.item()  # Ensure rho is a scalar
        # Inverse of CDF of the marginal proportions (used as thresholds)
        phi_a = norm.ppf(p1)
        phi_b = norm.ppf(p2)

        # Define the covariance matrix for the bivariate normal distribution
        cov_matrix = np.array([[1, rho], [rho, 1]])

        # Compute probabilities for each quadrant of the 2x2 table
        prob_11 = multivariate_normal.cdf([phi_a, phi_b], mean=[0, 0], cov=cov_matrix)
        prob_10 = norm.cdf(phi_a) - prob_11
        prob_01 = norm.cdf(phi_b) - prob_11
        prob_00 = 1 - prob_11 - prob_10 - prob_01

        # Ensure no probabilities are zero or negative
        if prob_11 <= 0 or prob_10 <= 0 or prob_01 <= 0 or prob_00 <= 0:
            return np.inf  # Return a large value if any probability is invalid

        # Log likelihood
        return -(a * np.log(prob_11) + b * np.log(prob_10) + c * np.log(prob_01) + d * np.log(prob_00))

    # Minimize the negative log likelihood to estimate rho
    bounds = [(-1 + epsilon, 1 - epsilon)]
    result = minimize(neg_log_likelihood, x0=[0.0], bounds=bounds, method='L-BFGS-B')
    return result.x[0]  # Return the estimated correlation


# Function to calculate tetrachoric correlation matrix
def tetrachoric_corr_matrix(df):
    cols = df.columns
    corr_matrix = pd.DataFrame(np.zeros((len(cols), len(cols))), index=cols, columns=cols)

    for i in range(len(cols)):
        for j in range(i, len(cols)):

            # Create a 2x2 contingency table for the two variables
            table = pd.crosstab(df.iloc[:, i], df.iloc[:, j]).values
            if table.shape == (2, 2):
                corr = tetrachoric_corr_2x2_table(table)
                corr_matrix.iloc[i, j] = corr
                corr_matrix.iloc[j, i] = corr
            else:
                corr_matrix.iloc[i, j] = np.nan
                corr_matrix.iloc[j, i] = np.nan
    return corr_matrix


# Example usage with random binary data
data = {
    'Var1': np.random.randint(0, 2, 100),
    'Var2': np.random.randint(0, 2, 100),
    'Var3': np.random.randint(0, 2, 100),
}

# Create a DataFrame
df = pd.DataFrame(data)

# Calculate tetrachoric correlation matrix
tetrachoric_corr = tetrachoric_corr_matrix(df)
print(tetrachoric_corr)