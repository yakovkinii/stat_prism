# Regression

Predicts one outcome from one or more predictors, with optional moderation and mediation.
Three model types are available: **linear (OLS)** for a numeric outcome, **binary logistic**
for a two-category outcome, and **multinomial logistic** for an unordered outcome with three
or more categories.

## When to use it

To model how an outcome depends on several variables at once — for example, predicting a
test score from age and income — and to estimate each predictor's unique contribution.

## Inputs

- **Dependent** — the outcome: numeric for linear, two categories for binary logistic, or
  three-plus categories for multinomial logistic.
- **Independent** — one or more predictors.
- **Moderator (optional)** — adds an interaction (moderation model).
- **Mediator (optional)** — fits a mediation model with indirect paths.

Moderation and mediation are mutually exclusive.

## Options

- **Model** — Linear (OLS), Logistic (binary), or Multinomial (logistic).
- **Standardised coefficients** — reports standardised (β) alongside unstandardised
  estimates (linear model).
- **Diagnostics** — an influence table (**Mahalanobis distance**, **Cook's distance**,
  **leverage**, **studentized residuals**, flagging the observations that exceed the usual
  cut-offs) plus the **Durbin–Watson** autocorrelation statistic and residual plots. This is
  a *report only* — nothing is excluded from the model.
- **Verbal indicators** (in-table columns), **Verbal report** (dropdown for how much written
  interpretation: None / Key findings / Significant only / Full), and **Plots**.

## Output

- A **model fit** table (R², adjusted R², F, *p* for OLS; pseudo-R² and a likelihood-ratio
  χ² for the logistic models).
- A **coefficients** table (estimates, standard errors, *t*/*z*, *p*, CIs; standardised if
  requested; odds ratios for logistic). The multinomial model reports one coefficient block
  per non-reference category, each compared against the first category as the baseline.
- **Path tables** for mediation (plus an **X → M → Y path diagram** for a single-predictor
  mediation when plots are on — with arrow-colour, label-size and spread controls), **diagnostics**
  when enabled, and a plot.
- **Plots.** With a single predictor the plot is a scatter with the fitted line (plus simple slopes
  / mediation paths where relevant). With **several predictors** there is no 2-D scatter, so an
  **observed-vs-predicted** plot is drawn instead (each point is a case, plotted as its actual
  outcome against the model's prediction; points near the 45° line indicate a good fit).

## Using categorical predictors

Regression accepts only **numeric / ordinal** predictors. To include a **nominal** variable
(e.g. region), first convert it with **One-hot encoding** (see
{doc}`../data-processing/onehot`); the resulting 0/1 indicator columns can then be selected
as predictors.

## Notes

- Rows with any missing value in the used columns are dropped (list-wise).
- A predictor literally named `const` is not allowed (the model adds its own intercept).
