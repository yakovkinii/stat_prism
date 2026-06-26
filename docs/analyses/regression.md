# Regression

Fits a linear (OLS) model predicting one outcome from one or more predictors, with optional
moderation and mediation.

## When to use it

To model how an outcome depends on several variables at once — for example, predicting a
test score from age and income — and to estimate each predictor's unique contribution.

## Inputs

- **Dependent** — the numeric outcome.
- **Independent** — one or more predictors.
- **Moderator (optional)** — adds an interaction (moderation model).
- **Mediator (optional)** — fits a mediation model with indirect paths.

Moderation and mediation are mutually exclusive.

## Options

- **Standardised coefficients** — reports standardised (β) alongside unstandardised
  estimates.
- **Diagnostics** — model checks such as influence measures and the Durbin–Watson statistic.
- **Verbal indicators** and **Plots**.

## Output

- A **model fit** table (R², adjusted R², F, *p*).
- A **coefficients** table (estimates, standard errors, *t*, *p*, CIs; standardised if
  requested).
- **Path tables** for mediation, **diagnostics** when enabled, and a plot.

## Using categorical predictors

Regression accepts only **numeric / ordinal** predictors. To include a **nominal** variable
(e.g. region), first convert it with **One-hot encoding** (see
{doc}`../data-processing/onehot`); the resulting 0/1 indicator columns can then be selected
as predictors.

## Notes

- Rows with any missing value in the used columns are dropped (list-wise).
- A predictor literally named `const` is not allowed (the model adds its own intercept).
