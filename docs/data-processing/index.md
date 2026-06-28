# Preparing data

Data-processing steps clean and reshape your data before analysis. Each step is added to
the **chain**: it takes the data from the step before it and produces a new version, leaving
the original untouched. You can stack as many steps as you need, reorder them, and turn some
of them on or off.

## How processing steps work

- **Data source.** Like analyses, each step reads from a source. **Auto** means "the output
  of the previous step", so a chain flows naturally from one step to the next.
- **Most steps add a new column** and leave the source column in place (for example, *Group
  Values*, *One-hot encoding*). A few replace a column **in place** (*Transform Column*) or
  remove rows (*Filter*, the outlier steps, *Response Quality*, *Impute ▸ Remove rows*).
- **Toggleable steps.** *Filter*, the outlier steps, and *Response Quality* have an
  enable/disable switch on their card, so you can compare results with and without them without
  deleting the step.
- **Previewing** a step shows its output; row-removing steps display removed rows in red.

The pages below describe each step.

```{toctree}
:maxdepth: 1

preprocess
transform
calculate-scale
invert-scale
formula
group
onehot
split-multiselect
filter
impute
outliers
grouped-outliers
nd-outliers
response-quality
select-id
bootstrap
```
