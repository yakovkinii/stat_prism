# Descriptive statistics

Summarises one or more variables — central tendency, spread, distribution shape — and
optionally produces frequency tables, normality tests, and a range of plots.

## When to use it

To describe your sample before (or alongside) inferential tests: means and standard
deviations for numeric variables, counts for categories, and figures that show each
variable's distribution.

## Inputs

- **Variables** — the columns to summarise. Numeric and ordinal columns get a quantitative
  summary; nominal columns get frequency tables and category charts.
- **Grouping (optional)** — a categorical column to split every summary by group.

## Options

Tables
: **Extended statistics** adds skewness, kurtosis, quartiles, and more to the basic
  N / mean / SD / median. **Frequency table** lists category counts (for categorical
  variables, split by group when grouping is set). **Normality test** runs Shapiro–Wilk,
  Kolmogorov–Smirnov, or Anderson–Darling, with optional verbal indicators of normality.

Plots
: **Distribution** (histogram, with an optional KDE smoothing curve and control over bin
  width), **Box plot** (optionally marking outliers), **Q–Q plot**, **Frequency bars**, and
  **Pie chart**. Ordinal variables can also get a pie chart in their defined order.

Verbal output
: Two independent toggles. **Verbal indicators in tables** adds in-table verbal columns (for
  example a *Normal?* conclusion in the normality table). **Plain-language summary (prose)** adds
  the written sentences — the outlier report, the normality summary, and the grouped-frequency
  summary. Enable either, both, or neither.

Other
: **Number columns** for compact wide tables.

## Output

- A **numeric summary** table (per group when grouping is on).
- An **outlier report** beneath the summary (when the plain-language summary is on), naming
  each outlier and listing their IDs for easy follow-up.
- A **normality** table (if requested).
- **Frequency** tables and the requested **plots**.

## Notes

- Ordinal columns are scored numerically for the quantitative summary but keep their labels
  and order in frequency tables and pie charts.
- Bin-width and KDE controls only apply when the distribution plot is shown.
