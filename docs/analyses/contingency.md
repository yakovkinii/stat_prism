# Contingency tables

Cross-tabulates two categorical variables and tests whether they are associated.

## When to use it

To relate two categorical questions — for example, region by preference, or gender by a
yes/no outcome.

## Inputs

- **Row variable** — one categorical column.
- **Column variable** — a second categorical column.

## Options

- **Continuity correction** — applies Yates' correction (2×2 tables only).
- **Effect size** — Cramér's V / phi.
- **Verbal indicators** — plain-language interpretation.
- **Paired data (symmetry test)** — for a square table of the same categories measured twice,
  runs a symmetry test (McNemar / Bowker) instead of the standard independence test.
- **Plots** — a distribution chart of the cross-tabulation.

## Output

- The **counts** table (the cross-tabulation).
- A **chi-square** test of independence with df and *p*, plus an effect size.
- **Fisher's exact** test for small 2×2 tables.
- Optional plot.

## Notes

- Both variables need at least two categories with data.
- Remember that blank text answers are read as a literal `nan` category; clean those first
  (e.g. with **Filter**) if you don't want them as a row/column.
