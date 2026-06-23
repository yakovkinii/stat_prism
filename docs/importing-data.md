# Importing data

StatPrism reads spreadsheet exports — the kind you get from survey tools such as Google
Forms, or any `.xlsx` / `.csv` file.

## Opening a file

Use **File ▸ Open…** and choose your file. StatPrism supports:

- `.xlsx` Excel workbooks (if a workbook has several sheets, you'll be asked which one to
  load),
- `.csv` files,
- `.sp` StatPrism project files (these reopen a whole saved session — see
  {doc}`projects-and-settings`).

The loaded data becomes the **raw data** at the start of your chain.

## What a Google Forms export looks like

A Forms response sheet usually has:

- a **Timestamp** column first,
- one column per question, with the **full question text as the header**,
- multiple-choice answers as plain text,
- "select all that apply" (checkbox) answers as a **comma-separated list in one cell**,
- linear-scale answers as numbers.

StatPrism reads all of this as-is. You don't need to rename or reshape anything before
importing.

## The ID column

On import, StatPrism adds a mandatory **ID** column (1, 2, 3, …) as the first column. It
uniquely identifies each respondent/row and is used, for example, to list which respondents
are outliers. You don't have to do anything with it.

If your file already contained a column literally named `ID`, it is kept but renamed out of
the way so the automatic identifier can take that name. If you would rather use one of your
own columns as the identifier, use the **Select ID** processing step (see
{doc}`data-processing/select-id`).

## Column types

Every column has a **type** that controls how StatPrism treats it and which analyses will
accept it:

Numeric
: Quantities and scores (age, income, test score, a 1–5 scale treated as a number).

Nominal
: Unordered categories (gender, region).

Ordinal
: Ordered categories (education level; a Likert scale treated as ordered labels).

ID
: The identifier column.

On import, StatPrism infers a type from the data: numbers become **Numeric**, text becomes
**Nominal**. Dates/timestamps are read as text.

```{important}
A blank answer in a **text** column is read as the literal value `nan` rather than a true
"missing". A blank answer in a **numeric** column stays genuinely missing. If you plan to
analyse a question that has skipped answers, check how its blanks were read in the data
viewer, and use **Impute Missing** or **Filter** if you need to handle them.
```

## Setting a column to Ordinal (and its order)

Many questionnaire items are ordered (e.g. *High school < Bachelor < Master < PhD*). To
have StatPrism respect that order in tables and charts, set the column to **Ordinal** and
define the category order with the **Transform Column** step (see {doc}`data-processing/transform`).
Ordinal columns are scored numerically where an analysis needs numbers (e.g. correlations),
and keep their labels and order in frequency tables and pie charts.

## Colour tags

Columns can carry a soft **colour tag** that follows them through the app and into exported
Excel headers, which helps when you have many variables. Colours from a source sheet's
coloured header cells are picked up automatically on import.

## Viewing and checking the data

Open the **data viewer** to see the imported table, confirm column types, and spot how
blanks were read. After adding cleaning steps, previewing a step's data shows the effect of
that step — for example, **Filter** and **Outliers** show removed rows in red.

## Replacing the data

You can load a different file at any time. Note that this resets the chain, so re-import
before building your processing steps and analyses.
