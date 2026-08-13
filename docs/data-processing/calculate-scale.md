# Calculate Scale

Builds a new scale column by aggregating the selected item columns per row:

- **Sum** or **Mean** across the items.
- Optionally **normalize** the result — Z-score, Stanine, Center, Min-max, Log, or Rank.
  *Stanine* is the normalized 1–9 score (mean 5, SD ≈ 2) from each value's percentile rank,
  using the standard stanine bands (not a linear rescale).
- The source questions can be kept, deleted, or auto-renamed.

**Color** tags the new scale column and its item columns. Leaving the color unset (**None**)
means "no change" — the items keep their existing color tags rather than being cleared.

**Reverse-keyed items** — put any reverse-scored questions in the **Reverse-score first**
field. They are flipped (using the same reference as {doc}`invert-scale` — auto-inferred as
*max + min* over their pooled values, or a **Manual** override you can **Preview**) and then
aggregated together with the normal questions. With **Replace reverse-scored columns with
flipped** on (default), those source columns are written back flipped and renamed
`… (flipped)` — unless the questions are **auto-renamed**, in which case they simply take the
`<scale> Q1`, `<scale> Q2` … names.

**Missing values** controls respondents who skipped some items:

- **Skip respondent** (default) — a row missing **any** item gets no scale value.
- **Allow up to max %** — aggregate over the items that are present, as long as the share of
  missing items is within **Max missing %**. For example, `0` keeps only complete respondents,
  `100` always aggregates over whatever is present, and `25` allows up to a quarter of items to
  be missing.
