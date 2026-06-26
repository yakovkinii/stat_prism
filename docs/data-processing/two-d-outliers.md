# Outliers in two dimensions

Drops rows that are **multivariate** outliers across **two** columns together — unusual
combinations that per-column checks miss. (A point can sit within the normal range on each
variable on its own, yet be an outlier for the *pair* because it breaks their typical
relationship.)

- Choose **Column 1** and **Column 2** (the two value columns).
- A row is dropped when its (x, y) pair lies too far from the joint centre, measured by the
  **Mahalanobis distance** (which accounts for the correlation between the two columns).
  The cutoff is the chi-square value at 95% confidence (df = 2).

A few points with non-degenerate spread are needed to estimate the covariance. Like the other
outlier steps, this one is toggleable, and removed IDs are listed.

To judge outliers one column at a time, use {doc}`outliers`; to judge within subgroups, use
{doc}`grouped-outliers`.
