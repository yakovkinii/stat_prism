# Correlation

Measures how strongly variables move together, as a correlation matrix with significance
and (where defensible) confidence intervals.

## When to use it

To quantify the association between two or more variables — for example, whether higher
scores on one item go with higher scores on another.

## Inputs

- **Variables** — two or more columns for the main matrix.
- **Control variables (optional)** — turns the analysis into a **partial correlation**,
  holding these constant (Pearson or Spearman only).
- **Second variable set (optional)** — produces a rectangular **cross** matrix of the first
  set against the second, instead of a square matrix.

## Options

Coefficient
: **Pearson** (linear), **Spearman** and **Kendall** / **Kendall tau-c** (rank-based),
  **Phi** / **Tetrachoric** (binary), **Polychoric** (ordinal).

Table
: **Compact** vs full layout; **Confidence intervals** (95%, via the Fisher-z transform for
  Pearson and Spearman); **Report only significant** to trim the verbal summary; **Number
  columns** for wide matrices.

Plots
: **Heatmap** of the matrix, and pairwise **scatter plots** with a regression line and its
  standard-error band.

## Output

- The **correlation matrix** with coefficients, significance, degrees of freedom, and
  optional CIs.
- A **verbal report** describing each association.
- Optional **heatmap** and **scatter** figures.

## Notes

- Confidence intervals are shown only where they are statistically defensible — Pearson and
  Spearman. Other coefficients show no CI.
- A column with **no variance** (a single repeated value) has an undefined correlation; its
  cells are left blank and a note explains why.
- Choosing Pearson on ordinal data triggers a warning, since rank-based coefficients are
  usually more appropriate there.
