# Glossary

Plain-language definitions of terms used in this guide and in StatPrism's output.

p-value
: The probability of seeing a result at least as extreme as the one observed if there were
  really no effect. Small values (commonly < .05) are taken as evidence against "no effect".

Confidence interval (CI)
: A range that, under repeated sampling, would contain the true value a stated percentage of
  the time (StatPrism reports 95% CIs). Wider intervals mean more uncertainty.

Effect size
: How *big* an effect is, independent of sample size — e.g. Cohen's *d* (mean differences),
  *r* (correlation), η²/η²p (ANOVA), Cramér's V (contingency). Significance says whether an
  effect exists; effect size says whether it matters.

Degrees of freedom (df)
: A count tied to sample and model size that calibrates a test's reference distribution.

Numeric / Nominal / Ordinal
: Column types. **Numeric** = quantities; **Nominal** = unordered categories; **Ordinal** =
  ordered categories. See {doc}`importing-data`.

Missing data
: Cells with no answer. In numeric columns these stay genuinely missing; in text columns a
  blank is read as the literal `nan`. Handle with **Impute Missing** or **Filter**.

Parametric vs non-parametric
: Parametric tests (t-test, ANOVA, Pearson) assume things like normality; non-parametric
  tests (Mann–Whitney, Kruskal–Wallis, Wilcoxon, Friedman, Spearman) make fewer assumptions
  and use ranks.

Normality
: Whether a variable approximately follows a bell-shaped (normal) distribution — an
  assumption of several parametric tests. Checked with Shapiro–Wilk, Kolmogorov–Smirnov, or
  Anderson–Darling.

Homogeneity of variance
: Whether groups have similar spread — an assumption of the standard t-test/ANOVA. Welch's
  versions relax it.

Correlation
: The strength and direction of association between two variables, from −1 to +1.
  **Pearson** measures linear association; **Spearman**/**Kendall** measure rank (monotonic)
  association.

Partial correlation
: The association between two variables after removing the influence of one or more control
  variables.

Reliability (Cronbach's α / McDonald's ω)
: How consistently a set of items measures the same thing. Higher is better; very low values
  suggest the items don't form a coherent scale. See {doc}`analyses/reliability`.

Factor / loading
: In factor analysis, a **factor** is an underlying dimension; a **loading** is how strongly
  an item reflects a factor. See {doc}`analyses/factor-analysis`.

Statistical power
: The chance a study will detect an effect that is really there. Power analysis relates power,
  sample size, effect size, and significance level. See {doc}`analyses/power-analysis`.

Standardised coefficient (β)
: A regression coefficient expressed in standard-deviation units, so predictors on different
  scales can be compared.

One-hot / indicator column
: A 0/1 column marking whether a category applies. Created by **Encode Categories** (from a
  single-select column) or **Split Multi-Select** (from a checkbox question).

APA style
: The American Psychological Association's formatting conventions for tables and statistics,
  widely used in the social sciences. StatPrism formats output to match.
