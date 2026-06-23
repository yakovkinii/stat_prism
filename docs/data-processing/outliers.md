# Outliers

Drops rows whose value on **any** selected column is an outlier.

- **IQR:** outside Q1 − 1.5×IQR … Q3 + 1.5×IQR.
- **Z-score:** |z| > 3.

When an ID column is present, the removed IDs are listed. Toggle the step off to keep all
rows.

To judge outliers separately within each subgroup, use {doc}`grouped-outliers` instead.
