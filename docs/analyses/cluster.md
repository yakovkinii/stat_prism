# Cluster analysis

Groups respondents into clusters based on their values across several variables.

## When to use it

To find natural segments in your sample — for example, grouping respondents by a profile of
scores.

## Inputs

- **Variables** — the numeric/ordinal columns that define similarity between respondents.

## Options

- **Method** — **K-means** or **Hierarchical**.
- **Linkage** (hierarchical) — Ward, Complete, Average, etc.
- **Number of clusters**.
- **Standardise variables** — z-scores each variable first, so variables on larger scales
  don't dominate the distance.
- **Show assignments** — adds a per-respondent cluster table.
- **Verbal indicators** (in-table columns), **Verbal report** (dropdown for how much written
  interpretation), and **Plots**.

## Output

- **Cluster sizes** and **centroids** (the average profile of each cluster).
- A **silhouette** score indicating how well-separated the clusters are.
- A 2-D **cluster scatter** (via PCA), a **dendrogram** for hierarchical clustering, and a
  **k-selection** plot to help choose the number of clusters.
- Per-respondent **assignments** (if enabled).

## Notes

- Results are reproducible — the clustering and 2-D projection use a fixed random seed.
- Standardising is usually advisable when variables are on different scales.
