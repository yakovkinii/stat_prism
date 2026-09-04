# Organizing and cleaning your data

Real survey exports are rarely tidy. This guide shows the point-and-click ways to fix and organize
your columns before you analyze them. Do as much or as little as you need — each fix is its own
step, and everything downstream updates on its own.

## Fixing wrong answers (mapping)

Sometimes a respondent types something that doesn't belong — for example, in an "enter your age"
question someone writes the word *thirty* instead of `30`. You can correct these without editing the
spreadsheet by hand:

1. Add a {doc}`../data-processing/preprocess` step.
2. On that column, click **Map values…**.
3. Find the odd answer and type what it should become (e.g. `thirty` → `30`).

The same trick converts text answers to numbers (e.g. *Strongly agree* → `5`).

## Turning numbers into groups

You can also bundle a numeric column into categories — for example, split **age** into `<25`,
`25–40`, and `40+`. Use a {doc}`../data-processing/group` step: pick the column and define the cut
points. This is handy for making group comparisons or contingency tables later.

## Renaming columns

Long questions make awful column names. Two easy ways to rename:

- **By hand:** in {doc}`../data-processing/preprocess`, click a column's name and type a shorter
  one (e.g. `Q1`). Press **Tab** in the empty field to bring back the original.
- **Automatically:** when you build a scale with {doc}`../data-processing/calculate-scale`, choose
  the **auto-rename** option and its items are renamed neatly for you (`Scale Q1`, `Scale Q2`, …).

## Coloring columns

Columns can carry a **color tag**. Give all the items of one questionnaire the same color and they
become easy to spot — and much easier to pick out in a column selector when several questionnaires
are mixed together. You can set colors in {doc}`../data-processing/preprocess`, and
{doc}`../data-processing/calculate-scale` makes it easy to recolor a whole set of items at once.

## Reordering columns

If a subscale uses only the first few questions, its new column can end up stranded in the middle of
your dataset. Add an {doc}`../data-processing/arrange` step and drag the columns into whatever order
you like — for example, move that scale to the end so all the raw items stay together. It's a plain
drag-and-drop list, and columns are shown in their tag colors.

## Missing values and outliers

Two more things you can do, in passing:

- **Missing answers** can be filled in with {doc}`../data-processing/impute` (for example, replace
  blanks with the column's median).
- **Outliers** (unusually extreme values) can be checked with several methods — see
  {doc}`../data-processing/outliers`.

You don't need these for every study; reach for them only when your data calls for it.
