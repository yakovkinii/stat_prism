# Paired / repeated measures

Compares two or more **conditions measured on the same respondents** (within-subject), held
in separate columns.

## When to use it

When each row has several measurements to compare – for example, a pre-test and a post-test
column, or three time points – rather than separate groups of people.

## Inputs

- **Conditions**: two or more numeric columns, one per condition/time point.

With two conditions you get a paired test; with three or more, a repeated-measures test.

## Options

Method
: **Detect automatically**, **Parametric** (paired *t* / repeated-measures ANOVA), or
  **Non-parametric** (Wilcoxon signed-rank / Friedman).

Assumption checks
: **Auto / Yes / No** – the normality check on the differences (plus a sphericity check for
  three or more conditions). (With *Detect automatically*, assumption checks must be on.) The
  assumptions table is shown only when the **parametric** family is used; a non-parametric
  (rank-based) test does not rely on them, so no assumptions table is produced for it.

Other
: **Effect size / post-hoc**, **Verbal indicators** (in-table columns), **Verbal report**
  (dropdown for how much written interpretation: None / Key findings / Significant only /
  Full), **Number conditions**, and **Plots**. When plots are on, **Plot significant only** is
  on by default and shows the condition plot only when the selected paired/repeated-measures
  test is significant.

## Output

- A **descriptives** table across conditions.
- A **normality** (and, for three or more conditions, **sphericity**) table — only on the
  parametric route, when checks are on.
- The **test** result with the appropriate statistic, *p*, and effect size (e.g. Cohen's
  *d*z, generalized eta-squared, Kendall's *W*, or rank-biserial correlation).
- Post-hoc comparisons for three or more conditions.

## Notes

- Rows missing any condition are dropped (complete-case analysis), so all conditions are
  compared on the same respondents.
