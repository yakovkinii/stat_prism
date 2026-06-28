# ND outliers (multidimensional)

Flags **multivariate** outliers across several columns at once — unusual *combinations* that
per-column checks miss. (A point can sit within the normal range on each variable on its own,
yet be an outlier for the set because it breaks their typical relationship.)

- Select **two or more** columns in the single **Columns** field. With only one column selected
  the step flags an error.
- A row is flagged when its point lies too far from the joint centre, measured by the
  **Mahalanobis distance** (which accounts for the correlations between the columns). The cutoff
  is the chi-square value at 95% confidence, with degrees of freedom equal to the number of
  columns.

Flagged rows appear as checkboxes under **Remove:** (all ticked); untick any to keep that
respondent, and previewing the data shows the removed rows in **red**. A few points with
non-degenerate spread are needed to estimate the covariance. The step is also toggleable.

To judge outliers one column at a time, use {doc}`outliers`; within subgroups, use
{doc}`grouped-outliers`.
