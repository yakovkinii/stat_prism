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

- **Correlation** — **Pearson** (from the raw data) or **Polychoric** (tetrachoric for binary
  items), the latter estimated in-house and better suited to ordinal Likert items. The chosen
  matrix drives the KMO/Bartlett checks, the eigenvalues, and the extraction.
- **Extraction method** — Minimum Residual (MINRES), Maximum Likelihood (ML), or Principal
  Axis (PAF).
- **Rotation** — none, varimax, promax, oblimin, quartimax, and others (oblique rotations
  allow correlated factors).
- **Number of factors** — how many to extract.
- **Factor names** — optional comma-separated labels for the factors (e.g. `Anxiety, Mood`).
  They replace the default `F1`, `F2` … in every table and the loadings heatmap; blank or
  missing entries keep the default for that factor.
- **Kaiser normalisation**, **Verbal indicators in tables** (adds a plain-language column to the
  sampling-adequacy table — a KMO/MSA adequacy word per row and a significance verdict for
  Bartlett), **Number columns**, **Verbal report** (dropdown for how much written interpretation),
  and **Plots**.

## Output

- **Sampling adequacy** — KMO (overall and per item) and Bartlett's test, with plain-language
  adequacy labels when verbal indicators are on.
- **Eigenvalues** and a **scree plot**.
- **Factor loadings** with communalities and uniquenesses, plus a loadings **heatmap**.
- **Factor correlations** and a structure matrix for oblique rotations.

## Notes

- The number of factors cannot exceed the number of variables, and you need enough complete
  cases for a stable solution.
