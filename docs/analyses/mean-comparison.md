# Comparing groups (t-test / ANOVA)

Compares a numeric measure across **independent groups** and routes automatically to the
right test family: two groups → a t-test, three or more → ANOVA.

## When to use it

When a grouping variable splits respondents into separate groups (e.g. passed vs. failed,
or region A/B/C) and you want to know whether a measure differs between them.

## Inputs

- **Dependent variable(s)** — the numeric measure(s) to compare. You can list several.
- **Grouping** — exactly one categorical column defining the groups.

## Options

Method
: **Detect automatically**, **Parametric homogeneous** (Student's t / standard ANOVA),
  **Parametric inhomogeneous** (Welch's), or **Non-parametric** (Mann–Whitney for two
  groups / Kruskal–Wallis for more).

Assumption checks
: **Auto / Yes / No** — runs checks such as Levene's test for equal variances and a
  normality check. (With *Detect automatically*, assumption checks must be on so the method
  can be chosen.)

Other
: **Effect size** (Cohen's *d* for two groups; η² / partial η² for ANOVA), **Confidence
  intervals**, handling of **missing grouping values**, **Verbal indicators** (in-table
  columns), **Verbal report** (dropdown for how much written interpretation: None / Key
  findings / Significant only / Full), **Number columns**, and **Plots**.

## Output

- A **descriptives-by-group** table.
- The **test** result with statistic, df, *p*, and (if requested) effect size and CI.
- **Assumption-check** results when enabled.
- A post-hoc comparison for ANOVA where applicable.

## Notes

- Groups need a minimum number of cases; very small groups are reported as insufficient.
- For comparing **conditions measured on the same people** (repeated measures), use
  {doc}`paired` instead.
