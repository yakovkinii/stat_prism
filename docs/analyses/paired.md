# Paired / repeated measures

Compares two or more **conditions measured on the same respondents** (within-subject), held
in separate columns.

## When to use it

When each row has several measurements to compare — for example, a pre-test and a post-test
column, or three time points — rather than separate groups of people.

## Inputs

- **Conditions** — two or more numeric columns, one per condition/time point.

With two conditions you get a paired test; with three or more, a repeated-measures test.

## Options

Method
: **Detect automatically**, **Parametric** (paired *t* / repeated-measures ANOVA), or
  **Non-parametric** (Wilcoxon signed-rank / Friedman).

Assumption checks
: **Auto / Yes / No** — includes a normality check on the differences. (With *Detect
  automatically*, assumption checks must be on.)

Other
: **Effect size / post-hoc**, **Verbal indicators**, **Number conditions**, and **Plots**.

## Output

- A **descriptives** table across conditions.
- A **normality** table (when checks are on).
- The **test** result with the appropriate statistic, *p*, and effect size (e.g. Cohen's
  *d*z, generalized eta-squared, Kendall's *W*, or rank-biserial correlation).
- Post-hoc comparisons for three or more conditions.

## Notes

- Rows missing any condition are dropped (complete-case analysis), so all conditions are
  compared on the same respondents.
