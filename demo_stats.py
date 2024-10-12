import statsmodels.api as sm
import pandas as pd


def regression_analysis(df, dependent_col, independent_cols, moderator_col=None, mediator_col=None):

    # Ensure only one of moderator_col or mediator_col is provided
    if moderator_col is not None and mediator_col is not None:
        raise ValueError("You can only specify either moderation or mediation, not both.")

    if moderator_col:
        print("Performing Moderation Analysis...\n")
        # Add interaction terms between the independent variables and the moderator
        original_independent_cols = independent_cols.copy()
        for ind_col in original_independent_cols:
            interaction_term = f"{ind_col}_x_{moderator_col}"
            df[interaction_term] = df[ind_col] * df[moderator_col]
            independent_cols.append(interaction_term)

    if mediator_col:
        print("Performing Mediation Analysis...\n")
        # Step 1: Regress mediator on independent variables
        X_mediator = sm.add_constant(df[independent_cols])
        mediator_model = sm.OLS(df[mediator_col], X_mediator).fit()

        # Display results for mediation step 1 (IVs -> Mediator)
        print("\nStep 1: Mediation - Regressing mediator on independent variables\n")
        print(mediator_model.summary())

        # Step 2: Regress dependent variable on independent variables and mediator
        independent_cols.append(mediator_col)

    # Fit the final regression model
    X = sm.add_constant(df[independent_cols])
    model = sm.OLS(df[dependent_col], X).fit()

    # Print essential results
    print("\nFinal Regression Results:")
    print(f"R-squared: {model.rsquared:.4f}")
    print(f"Adjusted R-squared: {model.rsquared_adj:.4f}")
    print("\nCoefficients:")
    for param_name, param_value in model.params.items():
        print(f"{param_name}: {param_value:.4f}")

    print("\nStandard Errors:")
    for param_name, std_err in model.bse.items():
        print(f"{param_name}: {std_err:.4f}")

    print("\nT-values:")
    for param_name, t_val in model.tvalues.items():
        print(f"{param_name}: {t_val:.4f}")

    print("\nP-values:")
    for param_name, p_val in model.pvalues.items():
        print(f"{param_name}: {p_val:.4f}")



# Example dataframe
data = {
    'Y': [1, 2, 3, 4, 5],
    'X1': [1, 0, 3, 2, 4],
    'X2': [5, 4, 3, 2, 1],
    'Moderator': [2, 3, 1, 4, 0],
    'Mediator': [1, 2, 2, 3, 4]
}
df = pd.DataFrame(data)

# Performing moderation analysis
regression_analysis(df, dependent_col='Y', independent_cols=['X1'], moderator_col='Mediator')

# Performing mediation analysis
# regression_analysis(df, dependent_col='Y', independent_cols=['X1', 'X2'], mediator_col='Mediator')
