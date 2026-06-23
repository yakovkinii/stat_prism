# Factor analysis

StatPrism provides **Exploratory Factor Analysis (EFA)** to uncover latent factors behind a
set of items, and **Confirmatory Factor Analysis (CFA)** to test a hypothesised structure.

## Exploratory Factor Analysis (EFA)

### When to use it

To discover how many underlying factors a battery of items reflects, and which items load on
which factor.

### Inputs

- **Variables** — two or more numeric/ordinal items.

### Options

- **Extraction method** — Minimum Residual (MINRES), Maximum Likelihood (ML), or Principal
  Axis (PAF).
- **Rotation** — none, varimax, promax, oblimin, quartimax, and others (oblique rotations
  allow correlated factors).
- **Number of factors** — how many to extract.
- **Kaiser normalisation**, **Number columns**, and **Plots**.

### Output

- **Sampling adequacy** — KMO (overall and per item) and Bartlett's test.
- **Eigenvalues** and a **scree plot**.
- **Factor loadings** with communalities and uniquenesses, plus a loadings **heatmap**.
- **Factor correlations** and a structure matrix for oblique rotations.

### Notes

- The number of factors cannot exceed the number of variables, and you need enough complete
  cases for a stable solution.

## Confirmatory Factor Analysis (CFA)

Tests how well a **pre-specified** factor structure fits the data, reporting standard fit
indices. Define which items load on which factor, then read the fit statistics to judge the
model. Use CFA when you already have a hypothesised measurement model (for example, from
prior EFA or theory).
