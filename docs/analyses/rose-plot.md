# Rose Plot

```{image} ../_static/img/rose-plot.png
:align: right
:width: 240px
:alt: Rose plot example
```

Draws a **rose plot** (a circular bar chart): one bar — a *ray* — per selected column, its
length set by the chosen aggregate of that column. It is a compact way to compare many
variables on a single radial scale.

## When to use it

To compare the typical level of several items at a glance — for example the mean of each
item in a profile, or the total of each category — on one circular figure instead of a row
of separate bar charts.

## Inputs

- **Columns (numeric / ordinal)**: one to twelve columns, one ray each.
- No grouping: the plot summarises each column across all respondents.

## Options

Aggregate
: **Mean**, **Sum**, or **Median** — the statistic that sets each ray's length. Each column
  is aggregated over all respondents; ordinal columns are read as their numeric face values
  and non-numeric cells are ignored.

Scale
: **Scale min** and **Scale max** set the radial axis limits. Left blank, they are chosen
  automatically from the data (the minimum is clamped to 0 when all values are non-negative).

Plot settings
: **Colors** — the colour map for the rays (`hsv`, `twilight`, `rainbow`, `turbo`, or **Auto**
  for the StatPrism palette). **Ray values** prints each ray's aggregate just outside the rim;
  **Decimal places** rounds those printed values to a fixed number of places — by default one
  more than the data's own precision (so an aggregate such as the mean keeps a useful digit),
  or **Off** for the full value — and **Value label distance** moves them further out from the
  rim. **Angular gap** adds space
  between the rays. **Trim long labels** shortens long column names in the legend. **Group
  shading** shades alternating blocks of *N* rays — and the matching legend rows — so groups are
  easy to count when there are many columns (off by default; **Shade color** and **Shade alpha**
  tune the band when it is on). The shared figure controls (size, fonts, colours) also apply.

## Output

- A **rose plot** figure: one colour-coded ray per column, each ray identified by colour in the
  legend, with its aggregate value printed at the rim (when **Ray values** is on).

## Notes

- Each ray is identified by its **colour** (see the legend), not by a number, so column names
  that already contain numbers do not clash with ray labels.
- Columns with no numeric values to aggregate are dropped from the plot.
- The plot embeds directly in copied and exported output, like every other StatPrism figure.
