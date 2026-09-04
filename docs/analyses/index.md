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

Most analyses share a few conveniences:

- **Verbal indicators** — adds in-table verbal columns (e.g. whether a result is statistically
  significant).
- **Verbal report** — a dropdown for how much plain-language prose to write: **None**, **Key
  findings**, **Significant only**, or **Full**. The amount of prose scales with how much
  there is to say, so large analyses stay readable.
- **Number columns** — replaces long variable names with numbered references in big tables
  and adds a legend, keeping wide tables readable.
- **Plots** — optional figures (histograms, box plots, heatmaps, scatter plots, …). Plots
  embed directly in copied/exported output. Where a plot can **number the variables** (a
  categorical axis, pie slices, or a heatmap), the number→name mapping is spelt out as a
  caption under the figure. Pie charts also expose separate sliders for the radial position
  of the percentages and of the slice names (move either outside the pie).
- **Confidence intervals / effect sizes** — where applicable, reported alongside the test.
- **Inline filters** — a per-analysis filter, added with the **Add filter** button in the analysis
  card's button row. It restricts the analysis to a subset of rows *without* adding a
  data-processing step to the chain, so it affects only this analysis. Each filter row (just under
  the title) shows its **condition** and how many **additional** rows it removes beyond the earlier
  filters, plus an eye button to **preview** those rows (shown in red) and a delete button. **Click
  the row** to configure it (the same options as the {doc}`../data-processing/filter` step, with a
  **Back** button to the analysis). Multiple filters combine with **AND** — a row is kept only if it
  passes every filter. The filter summary is included when you copy the analysis. If a filter's
  column later disappears, the row is outlined red and the analysis stops with an error until you fix
  or remove it.

Every result can be copied or exported — see {doc}`../results-and-export`.
