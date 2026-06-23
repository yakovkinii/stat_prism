# Outliers within groups

Like {doc}`outliers`, but each value is judged against the distribution of **its own group**
rather than the whole sample.

- Choose the **value column(s)** and a **grouping** column.
- A row is dropped if it is an outlier (**IQR** or **Z-score**) within its group on any
  selected column.

Useful when groups differ in level or spread. Also toggleable, and removed IDs are listed.
