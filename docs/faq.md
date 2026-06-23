# FAQ & troubleshooting

**A column I want isn't offered in a selector.**
: Selectors only show columns of a compatible type. Check the column's **type** in the data
  viewer — for example, a numeric summary won't list a text column. Use **Transform Column**
  to change a column's type (see {doc}`data-processing`).

**My nominal variable won't go into a regression.**
: Regression accepts only numeric/ordinal predictors. Convert the nominal column with
  **Encode Categories (one-hot)** first; then select the resulting 0/1 indicator columns. See
  {doc}`analyses/regression`.

**A blank answer shows up as `nan`.**
: Blank cells in **text** columns are read as the literal value `nan`; blanks in **numeric**
  columns stay genuinely missing. Handle them with **Impute Missing** or remove them with
  **Filter**. See {doc}`importing-data`.

**A correlation cell is empty.**
: If a variable has **no variance** (one repeated value), its correlation is undefined and
  shown blank — a note explains this. Also, confidence intervals are only shown for Pearson
  and Spearman; other coefficients legitimately show none.

**My results didn't change after I edited a cleaning step.**
: Results read from a **data source**. With **Auto** they follow your latest step
  automatically; if you set a specific source, make sure it points where you intend.

**A group comparison says there aren't enough groups / cases.**
: The grouping column must define at least two groups, each with enough cases. Check the
  grouping column's values (watch for a stray `nan` category from blank answers).

**Tables/figures pasted into Word look wrong.**
: Use **File ▸ Copy All Results** and paste into a rich-text editor (Word). Set the
  **Language** and **Theme** before copying, since results render in the current settings.

**How do I share or archive a full report?**
: **File ▸ Export Report (HTML)…** writes one self-contained file (figures embedded). Open it
  in a browser to read or print to PDF.

**How do I reopen everything later?**
: Save a `.sp` **project** (**File ▸ Save As…**). It stores the data, all processing steps,
  and all analyses. See {doc}`projects-and-settings`.

**Is StatPrism free?**
: Yes — it is open source. Report issues or suggest features on the project's GitHub
  repository.
```{seealso}
New here? Start with {doc}`getting-started`, then follow the {doc}`worked-example`.
```
