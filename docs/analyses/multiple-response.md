# Multiple response

Summarises a "select all that apply" (checkbox) question whose options have been split into
0/1 indicator columns.

## When to use it

For a multi-select question where respondents could pick several options, and you want a
table of how often each option was chosen.

## Before you start

Run **Split Multi-Select** first (see {doc}`../data-processing/split-multiselect`) to turn the
raw comma-separated answers into one 0/1 indicator column per option. Multiple Response then
summarises those indicator columns.

## Inputs

- **Indicator columns (0/1)** — select all the indicator columns that came from one
  question.

## Options

- **Bar chart of counts** — a figure of selections per option.

## Output

A table with, per option:

- **Selected** — how many respondents chose it.
- **% of responses** — its share of all selections (these sum to 100%).
- **% of cases** — its share of respondents who chose at least one option (these sum to more
  than 100%, since a respondent can pick several).

Plus a total row, an optional explanatory note (via the **Verbal report** dropdown), and the
optional bar chart.

## Notes

- "Cases" excludes respondents who selected nothing.
- Any non-zero, non-missing value in an indicator column counts as "selected".
