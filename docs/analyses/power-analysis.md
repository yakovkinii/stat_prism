# Power analysis

Works out the relationship between significance level, statistical power, effect size, and
sample size for a chosen test — fixing three of them to solve for the fourth. **No data set
is needed.**

## When to use it

- Before a study, to plan the **sample size** needed to detect an effect.
- After (or while planning), to check the **power** of a given design, or the **effect size**
  it can detect.

## Inputs (all numbers you type)

- **Test type** — Two-sample t-test, Paired / one-sample t-test, One-way ANOVA, or
  Correlation.
- **Solve for** — Sample size, Power, or Effect size.
- **Alpha** (e.g. 0.05), **Power** (e.g. 0.80), **Effect size**, **Sample size** — provide
  the three you know.
- **Number of groups** — for ANOVA.
- **Tails** — two-sided or one-sided.

## Output

- The **solved quantity** with the inputs that produced it.
- A **power-vs-sample-size curve** for the chosen test.

## Notes

- Effect sizes follow Cohen's conventions: *d* for t-tests, *f* for ANOVA, *r* for
  correlation.
- t-tests and ANOVA use the standard non-central distributions; correlation uses the
  Fisher-z approximation.
