# Exploratory factor analysis

**Exploratory Factor Analysis (EFA)** uncovers the latent factors behind a set of items —
how many underlying factors a battery reflects, and which items load on which factor. Use it
when you do *not* yet have a hypothesised structure; to test a structure you already have,
see {doc}`confirmatory-factor-analysis`.

## When to use it

To discover how many underlying factors a battery of items reflects, and which items load on
which factor.

## Inputs

- **Variables** — two or more numeric/ordinal items.

## Options

- **Extraction method** — Minimum Residual (MINRES), Maximum Likelihood (ML), or Principal
  Axis (PAF).
- **Rotation** — none, varimax, promax, oblimin, quartimax, and others (oblique rotations
  allow correlated factors).
- **Number of factors** — how many to extract.
- **Kaiser normalisation**, **Number columns**, **Verbal indicators**, and **Plots**.

## Output

- **Sampling adequacy** — KMO (overall and per item) and Bartlett's test.
- **Eigenvalues** and a **scree plot**.
- **Factor loadings** with communalities and uniquenesses, plus a loadings **heatmap**.
- **Factor correlations** and a structure matrix for oblique rotations.

## Notes

- The number of factors cannot exceed the number of variables, and you need enough complete
  cases for a stable solution.
