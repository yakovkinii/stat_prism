# Structural equation modelling

Fits a **custom structural equation model (SEM)** that you specify yourself, using the
`semopy` backend. Use it when your model goes beyond a single confirmatory factor structure —
for example, latent factors that predict one another, or a mix of measurement and regression
paths.

The model is built entirely by clicking — no syntax to type.

## Building the model

**1. Measurement model — define the latent factors**
- Set the **Number of latent factors**, then click the observed columns that make up each factor
  into its **Factor _n_ indicators** field (a factor needs at least two indicators).
- Optionally name the factors with **Factor names** (comma-separated); otherwise they are
  `F1`, `F2`, …

**2. Structural model — add the paths**
- Under **Paths**, click **+ Add path** for each relationship. Each row is a single influence:
  pick a **From** node, a **Type** (**predicts →** for a regression or **covaries ↔** for a
  covariance), and a **To** node — every dropdown is a single choice.
- Add one row per predictor: several `X predicts Y` rows to the same outcome are combined into
  one regression, e.g. two rows `F1 predicts Y` and `F2 predicts Y` become `Y ~ F1 + F2`.

**Estimator** — Maximum Likelihood (ML) or Diagonally Weighted Least Squares (DWLS).

**Verbal indicators in tables** — when on, the fit table gains a plain-language quality column
(e.g. RMSEA → *good* / *acceptable* / *poor*, CFI/TLI → *excellent* / *acceptable* / *poor*), and
each path's estimate is tagged with significance stars (`*** p<.001, ** p<.01, * p<.05`).

**Verbal report** — an optional written interpretation below each table summarising the model
fit, which paths are significant and the strongest effect.

## Output

- A **model fit** table (the fit indices semopy reports — χ², degrees of freedom, CFI, TLI,
  RMSEA, and so on).
- A **parameter estimates** table: every directed and covariance path with its estimate, standard
  error, *p*-value and standardized value, labelled with your factor and column names. Directed
  effects are shown with an arrow (`predictor → outcome`) and covariances with a double arrow
  (`a ↔ b`).
- A separate **variances** table for the estimated variances (residual/error variances of items and
  factor variances), kept out of the main table since they are secondary. A variance is *not* a
  correlation — its unstandardized estimate is in the data's own units and is generally not 1. The
  standardized value is the informative one: for an item it equals the unexplained proportion
  (1 − R²), so a smaller value means the factor explains more of that item.
- With **Path diagram** on, a schematic of the fitted model: each factor node with arrows to its
  indicators (standardized loadings), plus the structural paths between factors — a **double arrow**
  (`↔`) for a factor covariance and a **single arrow** (`→`) for a directed regression, each
  labelled with its standardized coefficient. It reuses the CFA diagram's plot settings (spacing,
  arrow colour/label size, correlation-curve and plot-size sliders). Paths involving observed
  variables that are not a factor's own indicator are omitted from the picture but still listed in
  the estimates table.

## Notes

- Only complete numeric rows are used (list-wise deletion); ordinal columns are scored
  numerically.
- Covariances beyond the automatic residual variances (and any `↔` paths you add) are not
  specified in this version.
- Two kinds of degenerate path are ignored: a self-loop (**From** and **To** the same node) and a
  `factor → its own indicator` path, which would just duplicate a loading already implied by the
  measurement model. All other combinations are allowed — including an observed item predicting a
  factor (a MIMIC-style cause), a factor predicting another factor's item (a cross-loading), and
  item-with-item covariances (correlated residuals).
