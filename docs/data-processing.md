# Preparing data

Data-processing steps clean and reshape your data before analysis. Each step is added to
the **chain**: it takes the data from the step before it and produces a new version, leaving
the original untouched. You can stack as many steps as you need, reorder them, and turn some
of them on or off.

## How processing steps work

- **Data source.** Like analyses, each step reads from a source. **Auto** means "the output
  of the previous step", so a chain flows naturally from one step to the next.
- **Most steps add a new column** and leave the source column in place (for example, *Group
  Values*, *Encode Categories*). A few replace a column **in place** (*Transform Column*) or
  remove rows (*Filter*, *Outliers*, *Impute ▸ remove rows*).
- **Toggleable steps.** *Filter* and *Outliers* have an enable/disable switch on their card,
  so you can compare results with and without them without deleting the step.
- **Previewing** a step shows its output; row-removing steps display removed rows in red.

The rest of this page describes each step.

---

## Filter

Keeps only the rows that match a condition on one column.

- **Numeric columns:** keep rows where the value satisfies a comparison (`<`, `≤`, `=`, `≥`,
  `>`, `≠`) against a value. For `=`/`≠` you may list several values (comma/space separated)
  to keep/exclude any of them. You can also keep rows where the cell **is empty** or **is not
  empty**.
- **Categorical columns:** tick the category values to keep (an *(empty)* option appears when
  the column has blank cells).

Rows that don't match are removed downstream; previewing shows them in red. Toggle the step
off to keep all rows.

## Outliers

Drops rows whose value on **any** selected column is an outlier.

- **IQR:** outside Q1 − 1.5×IQR … Q3 + 1.5×IQR.
- **Z-score:** |z| > 3.

When an ID column is present, the removed IDs are listed. Toggle the step off to keep all
rows.

## Impute Missing

Fills missing cells in the selected columns, or removes rows that have missing values.

- **Mean** / **Median** — from the column's non-missing numeric values.
- **Mode** — the most frequent value.
- **Constant value** — a value you supply.
- **Remove rows** — drops rows missing any selected column.

"Missing" captures both blank strings and true `NaN`.

## Group Values

Bins a numeric column into ordered groups using split points you provide (e.g. split points
`30, 50` give three bins: under 30, 30–50, and 50+).

- **Split point goes to** controls which side a value exactly on a split point falls on —
  *Higher group* (left-closed `[a, b)`, the default) or *Lower group* (right-closed
  `(a, b]`).
- You can label the bins yourself or let StatPrism name them automatically.

The grouped column is added as a new **ordinal** column, leaving the original untouched.

## Transform Column

Reshapes one column **in place** (it is replaced, not duplicated). In order, it can:

1. **Map values** — recode specific values to new ones.
2. **Set the target type** — Nominal, Ordinal, or Numeric.
3. For **Ordinal**: define an explicit **category order**, and optionally **flip** the scale
   (reference − x; reference defaults to max + min).
4. For **Numeric**: apply a **normalisation** — Z-score, Stanine, Center, Min-max, Log, or
   Rank.
5. Set a **colour tag** and, optionally, a new name.

Use this to make a column ordinal with a proper order, to reverse-key an item, or to
standardise a variable before analysis.

## Invert Scale

Reverse-scores the selected columns: each value `x` becomes `reference − x`. With no
reference given, it uses `max + min` of the column, so a 1–5 Likert item maps 1↔5, 2↔4,
3↔3. Use it to fix reverse-keyed items before building a scale. The inverted values are
added as new columns.

## Calculate Scale

Builds a new scale column by aggregating the selected item columns per row:

- **Sum** or **Mean** across the items.
- Optionally convert the result to **Stanine** (1–9).
- The source questions can be kept, deleted, or auto-renamed.
- By default a row missing **any** item yields a missing scale value; enable **Aggregate
  despite missing values** to aggregate over the items that are present.

## Encode Categories (one-hot)

Turns a single-select **nominal** column with *k* categories into **0/1 indicator columns**
(one per category, named *column = category*). This lets a categorical variable be used as a
**regression predictor** (regression accepts only numeric/ordinal inputs).

- With **Drop reference category** on (default), one category is omitted (*k* − 1 columns)
  and becomes the baseline — the usual setup for regression.
- Turn it off to keep all *k* columns (useful for plain description).

A row with a missing value gets 0 in every indicator. The original column is left untouched
and the indicators are inserted right after it.

## Split Multi-Select

Splits a "select all that apply" / checkbox column — where each cell holds a delimited list
of chosen options (e.g. *"Email, Calendar"*) — into one **0/1 indicator column per distinct
option**. A cell gets 1 for an option it contains and 0 otherwise; blank cells get 0
everywhere.

The new columns are numeric, so each can be summarised (its mean is the proportion who
chose that option) or correlated, and together they feed the **Multiple Response** analysis
(see {doc}`analyses/multiple-response`). Set the **delimiter** (comma by default) and an
optional name **prefix**.

## Select ID

Promotes one of your own columns to be the identifier (the **ID** column), replacing the
automatic one. The chosen column must have **no missing values** and **only unique values**.

## Other steps

StatPrism also includes a **Formula** step (compute a new column from an expression over
existing columns) and a **Preprocess** step (general tidying helpers), as well as a
**Bootstrap** step (generate resampled / correlated synthetic data — see below). Their
on-screen instructions describe the available options.

### Bootstrap (correlated resampling)

Generates new rows by resampling, optionally inducing a requested **rank correlation**
between variables while preserving each variable's distribution (its marginal). You nominate
a **reference** variable and one or more **drivers** that should correlate with it, and set
the target correlation for each. This is useful for simulations, teaching, and power/what-if
exploration. Because it draws random values, set up your analysis to expect sampling
variation.
