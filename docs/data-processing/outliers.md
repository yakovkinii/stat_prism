# Outliers

Drops rows whose value on **any** selected column is an outlier.

- **IQR:** outside Q1 − 1.5×IQR … Q3 + 1.5×IQR.
- **Z-score:** |z| > 3.

Flagged rows are listed as checkboxes under **Remove:** (all ticked by default). Untick any to
**keep** that respondent — useful when a value is extreme but legitimate. Previewing the data
shows the rows that will be removed in **red**. Toggle the step off to keep all rows.

To judge outliers separately within each subgroup, use {doc}`grouped-outliers`; across several
columns jointly, use {doc}`nd-outliers`.
