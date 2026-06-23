# Calculate Scale

Builds a new scale column by aggregating the selected item columns per row:

- **Sum** or **Mean** across the items.
- Optionally convert the result to **Stanine** (1–9).
- The source questions can be kept, deleted, or auto-renamed.
- By default a row missing **any** item yields a missing scale value; enable **Aggregate
  despite missing values** to aggregate over the items that are present.
