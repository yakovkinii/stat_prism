# Random sub-samples

Adds a nominal column that randomly assigns each row to a sub-sample label.

## When to use it

Use it when you need reproducible random assignment into groups, such as train/test splits,
experimental arms, or manual sub-samples with fixed sizes.

## Options

- **New column name** - the assignment column to create.
- **Assignment mode** - **Counts** for exact row counts, or **Percentages** for proportions.
- **Allocation** - one row per output value. Enter a count or percentage for every row except
  the last; the last row is always the remaining group.

## Output

The step appends one nominal column. The generated column keeps the allocation values in the
order shown in the settings.

## Notes

- Percentages are converted to integer row counts with largest-remainder rounding, so every
  input row receives exactly one label.
- Requested counts cannot exceed the number of rows. Percentages cannot exceed 100%.
- Assignment uses a fixed seed of `0`, so the same setup produces the same generated column.
