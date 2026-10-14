# Random sub-samples

Adds a nominal column that randomly assigns each row to a sub-sample label.

## When to use it

Use it when you need reproducible random assignment into groups, such as train/test splits,
experimental arms, or manual sub-samples with fixed sizes.

## Options

- **New column name** - the assignment column to create.
- **Assignment mode** - **Counts** for exact row counts, or **Percentages** for proportions.
- **Allocation** - one row per output value, with the requested count or percentage.
- **Fill remaining rows** - assigns any unallocated rows to the remaining value.
- **Remaining value** - the label used for rows not covered by the allocation.
- **Use fixed random seed** - when enabled, uses the entered seed. When disabled, the default
  seed is `0`, so the generated assignment is reproducible.

## Output

The step appends one nominal column. The generated column keeps the allocation values in the
order shown in the settings.

## Notes

- Percentages are converted to integer row counts with largest-remainder rounding, so every
  input row receives exactly one label.
- Requested counts cannot exceed the number of rows. Percentages cannot exceed 100%.
