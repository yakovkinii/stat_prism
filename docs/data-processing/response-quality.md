# Response quality

Screens respondents for **careless or low-quality answering** on the selected questions and
flags them for removal — the survey-data equivalent of the outlier steps, but aimed at *how*
someone answered rather than at extreme values.

Pick the questions to inspect and a **Check**:

- **Long string** *(default)* — the longest run of identical *consecutive* answers covers at
  least **Flag at % of items** of the questions (classic straightlining down a grid).
- **Duplicate entries** — rows that repeat an earlier row across the selected questions (the
  first occurrence is kept). Ignores the threshold below.
- **High missingness** — the respondent left at least that share of the selected items blank.
- **Low variability** — the respondent's single most-common answer covers at least that share
  of the items (little variation across questions, even if not consecutive).

The **Flag at % of items** control is shared by the three percentage-based checks (for example,
`50` flags a respondent when half the items are involved); it does not affect *Duplicate
entries*.

Flagged rows are listed as checkboxes under **Remove:** (all ticked by default). Untick any to
**keep** that respondent. Previewing the data shows the rows that will be removed in **red**, and
the step is toggleable from the card — so you can compare results with and without the cleaning.
