# Analysing data

Each analysis is a module you configure in the settings panel on the right; its results
appear as a card in the large area on the left. Every analysis lets you choose a **data
source** (default **Auto** = your latest
data) and the **columns** to analyse.

Pick the analysis that matches your question:

| You want to… | Use |
| --- | --- |
| Summarise variables (means, spread, distributions) | {doc}`descriptive` |
| Measure how two+ variables move together | {doc}`correlation` |
| Compare a measure across independent groups | {doc}`mean-comparison` |
| Compare conditions measured on the same people | {doc}`paired` |
| Relate two categorical variables | {doc}`contingency` |
| Predict an outcome from one or more variables | {doc}`regression` |
| Check the internal consistency of a scale | {doc}`reliability` |
| Discover the underlying factors behind a set of items | {doc}`exploratory-factor-analysis` |
| Test a hypothesised factor structure | {doc}`confirmatory-factor-analysis` |
| Fit a custom structural equation model | {doc}`sem` |
| Group respondents into clusters | {doc}`cluster` |
| Plan a sample size or check statistical power | {doc}`power-analysis` |
| Summarise a "select all that apply" question | {doc}`multiple-response` |

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

Every result can be copied or exported — see {doc}`../results-and-export`.
