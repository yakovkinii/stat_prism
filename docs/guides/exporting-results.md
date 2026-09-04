# Getting your results into Word (and elsewhere)

Once your tables and figures look right, here's how to get them out. See
{doc}`../results-and-export` for the reference; this is the quick how-to.

## What you can copy

Every result has copy buttons, so you can grab exactly what you need:

- **One element** — each table or figure has its own copy button (copies just that item).
- **A whole result** — the card's copy button copies all of that analysis's tables and figures
  together.
- **Everything** — **File ▸ Copy All Results** copies every result card at once, in order.

## Pasting into Word

For the cleanest result, paste as HTML:

1. Copy (one of the options above).
2. In Word, use **Paste Special ▸ HTML Format**. Tables come in as real, editable tables in APA
   style, and figures come in as images.

A **plain paste** (Ctrl+V) usually works too, but two things to watch for:

- **Remove the indent on the line you paste into.** Word's default first-line/left indent pushes
  the table columns out of alignment. Set the indent to **0** (Home ▸ Paragraph) for that spot, or
  clear the indent on the pasted table afterwards.
- Some columns may **lose their APA formatting** with a plain paste; Paste Special ▸ HTML keeps it.

```{tip}
Set the language (**Settings ▸ Language**) and plot theme (**Settings ▸ Plot theme**) *before*
copying — results are rendered in whatever language and theme are active.
```

## Saving a report file

**File ▸ Export Report (HTML)…** writes a single `.html` file with every table and figure built in.
It needs no other files, so you can open it in any web browser, email it, or print it to PDF.

## Exporting the data

**File ▸ Export data to Excel** saves the current (cleaned) table to `.xlsx`, with each column
header painted in its color tag — handy for sharing or double-checking in another program.
