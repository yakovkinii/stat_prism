# Building a scale with reverse-keyed items

A common task: several Likert items make up one scale, but some are **reverse-keyed** (worded in
the opposite direction), so they must be flipped before the items are combined. This guide takes you
from the raw spreadsheet to a finished scale column.

Suppose a 5-item wellbeing scale rated **1–5**, where items **Q2** and **Q4** are reverse-worded.

## 1. Import the data

**File ▸ Open…** and pick your `.xlsx`/`.csv` export. Open the **data viewer** to check that the
items loaded and that their **types** look right (see {doc}`../importing-data`). StatPrism adds an
**ID** column at the front automatically.

## 2. Tidy the items with Preprocess

Add a {doc}`../data-processing/preprocess` step to fix up the items in one place:

- **Rename** any awkward column names by clicking the name in place (e.g. a full question becomes
  `Q1`). Press **Tab** in the empty field to bring back the original name.
- If answers came in as **text** ("Strongly agree" … "Strongly disagree"), open **Map values…** on
  each item and map them to numbers `1`–`5`. Set the **type** to **Ordinal** (or **Numeric**) so
  the values are treated as a scale.
- Optionally give the scale's items a shared **color tag** so they are easy to spot later.

```{tip}
If **every** item shares the *same* text-to-number mapping, it's faster to select them all in a
single {doc}`../data-processing/transform` step and apply the mapping once, instead of mapping each
column in Preprocess.
```

You do **not** need to flip Q2/Q4 here — the Calculate Scale step does that in the next step, using
the correct reference.

## 3. Combine them with Calculate Scale

Add a {doc}`../data-processing/calculate-scale` step:

1. **Questions** field — put the **direct** (normally-keyed) items here: `Q1`, `Q3`, `Q5`.
2. **Reverse-score first** field — put the **reverse-keyed** items here: `Q2`, `Q4`. StatPrism
   flips them automatically before combining, so a high answer becomes a low one and a low answer
   becomes a high one. You can almost always leave this alone. (If your scale has a possible answer
   that nobody in your data happened to choose, the automatic flip can be slightly off — tick the
   box next to it and type the correct number to adjust it; the **Preview** shows the result.)
3. Give the new column a **name** (e.g. `Wellbeing`). Leaving it blank shows an error until you do.
4. Choose **Sum** or **Mean**, an optional **normalization** (e.g. Z-score or Stanine), and how to
   handle **missing values** (skip the respondent, or allow up to a set share of missing items).
5. Optionally set the new column's **color**.

That's it — a new `Wellbeing` column appears, with Q2/Q4 correctly reversed before aggregation. The
step's summary states which items were reverse-scored, and the source items can be kept, deleted, or
auto-renamed.

## 4. Use the scale

Point any analysis (for example {doc}`../analyses/descriptive`, {doc}`../analyses/correlation`, or
{doc}`../analyses/reliability` to check the scale's alpha) at the **Auto** data source and select
your new `Wellbeing` column.
