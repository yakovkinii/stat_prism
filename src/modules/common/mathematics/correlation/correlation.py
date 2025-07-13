#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, pearsonr, spearmanr

from src.modules.common.mathematics.correlation.binary_correlations import phi_coefficient, tetrachoric_corr_2x2_table
from src.modules.correlation.result import CorrelationType


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
            elif kind == CorrelationType.PHI:
                corr, p_value, degrees_of_freedom = phi_coefficient(valid_data[col1], valid_data[col2])
            elif kind == CorrelationType.TETRACHORIC:
                corr, _, p_value, degrees_of_freedom = tetrachoric_corr_2x2_table(
                    table=pd.crosstab(df.iloc[:, 0], df.iloc[:, 1]).values
                )
            else:
                raise ValueError(f"Invalid correlation type: {kind}")

            # Fill the square matrix
            correlation_matrix.loc[col1, col2] = corr
            p_matrix.loc[col1, col2] = p_value
            df_matrix.loc[col1, col2] = degrees_of_freedom

    return correlation_matrix, p_matrix, df_matrix
