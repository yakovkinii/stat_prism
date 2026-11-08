# Analyzing data

Each analysis is a module you configure in the settings panel on the right; its results
appear as a card in the large area on the left. Every analysis lets you choose a **data
source** (default **Auto** = your latest
data) and the **columns** to analyze.

Pick the analysis that matches your question:

| You want to… | Use |
| --- | --- |
| Summarize variables (means, spread, distributions) | {doc}`descriptive` |
| Measure how two+ variables move together | {doc}`correlation` |
| Compare a measure across independent groups | {doc}`mean-comparison` |
| Compare conditions measured on the same people | {doc}`paired` |
| Relate two categorical variables | {doc}`contingency` |
| Predict an outcome from one or more variables | {doc}`regression` |
| Check the internal consistency of a scale | {doc}`reliability` |
| Discover the underlying factors behind a set of items | {doc}`exploratory-factor-analysis` |
| Test a hypothesized factor structure | {doc}`confirmatory-factor-analysis` |
| Fit a custom structural equation model | {doc}`sem` |
| Group respondents into clusters | {doc}`cluster` |
| Plan a sample size or check statistical power | {doc}`power-analysis` |
| Summarize a "select all that apply" question | {doc}`multiple-response` |

```{toctree}
:maxdepth: 1
:hidden:

descriptive
multiple-response
contingency
correlation
mean-comparison
paired
regression
reliability
exploratory-factor-analysis
confirmatory-factor-analysis
sem
cluster
power-analysis
```

## Common options

Most analyses share several common options:

- **Verbal indicators**: adds in-table verbal columns (e.g. whether a result is statistically
  significant).
- **Verbal report**: a dropdown for how much plain-language prose to write, from least to most:
  **None** (no prose), **Headline** (one sentence naming the single standout result),
  **Key findings** (only the outstanding results), **Significant only** (every significant result),
  and **Full** (also the non-significant results). For analyses that produce many results (e.g.
  a correlation matrix, several group comparisons, a set of regression predictors) the prose is
  compacted rather than written one sentence per result – e.g. *"All correlations were significant
  except X and Y"* or *"Most predictors were significant (5 of 8)"* – with the full APA statistics
  kept for each result it names, so even large analyses stay readable. Analyses that produce a
  single result (reliability, cluster analysis, factor analysis, SEM) still layer the description:
  a one-line verdict at **Headline**, then progressively more facets as the level rises – the
  factor structure (clean vs. cross-loading items, how evenly the factors are filled), the
  sampling-adequacy and fit diagnostics, and, at **Full**, a methods note stating the choices that
  shaped the numbers (the coefficient type, estimator, rotation and extraction, clustering
  algorithm and linkage, and any applied modifications). (Power analysis is the exception: its
  single solved value carries the same short interpretation at every setting.)
- **Number columns**: replaces long variable names with numbered references in big tables
  and adds a legend, keeping wide tables readable.
- **Plots**: optional figures (histograms, box plots, heatmaps, scatter plots, …). Plots
  embed directly in copied/exported output. Where a plot can **number the variables** (a
  categorical axis, pie slices, or a heatmap), the number→name mapping is spelt out as a
  caption under the figure. Pie charts also expose separate sliders for the radial position
  of the percentages and of the slice names (move either outside the pie).
- **Confidence intervals / effect sizes**: where applicable, reported alongside the test.
- **Inline filters**: a per-analysis filter, added with the **Add filter** button in the analysis
  card's button row. It restricts the analysis to a subset of rows *without* adding a
  data-processing step to the chain, so it affects only this analysis. Each filter row (directly under
  the title) shows its **condition** and how many **additional** rows it removes beyond the earlier
  filters, plus an eye button to **preview** those rows (shown in red) and a delete button. **Click
  the row** to configure it (the same options as the {doc}`../data-processing/filter` step, with a
  **Back** button to the analysis). Multiple filters combine with **AND** – a row is kept only if it
  passes every filter. The filter summary is included when you copy the analysis. If a filter's
  column later disappears, the row is outlined red and the analysis stops with an error until you fix
  or remove it.

Every result can be copied or exported – see {doc}`../results-and-export`.
