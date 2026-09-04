# Making your figures look right

Every figure in StatPrism is adjustable — you don't have to accept the default look. This guide
shows where the controls are and how to fix the most common problem: text that overlaps.

## Where the settings are

Click a **figure** (or select its tab on a result card). Its **settings** appear in the panel on
the right. There's no code — just sliders, dropdowns, checkboxes, and color pickers. Change one and
the figure redraws immediately, so it's safe to experiment.

## What you can change

The exact controls depend on the figure, but you'll usually find:

- **Colors** — line, bar, and point colors, the frame/text color, and the background.
- **Font sizes** — separate sliders for the title, axis titles, tick labels, and legend.
- **Axis titles and labels** — type your own axis titles; rotate the x-axis labels; number the
  categories instead of naming them.
- **Line thickness, point size, transparency** — for scatter/line/box plots.
- **Overall size and shape** — a **Plot Size** slider (bigger for a report, smaller to fit) and an
  **Aspect** slider (taller vs. wider).
- **Gridlines, frame, margins** and more.

## Fixing overlapping or cut-off text

If labels overlap or run off the edge — usually because you have many columns or long column names —
you can almost always fix it by tweaking a setting or two:

- **Rotate the x-axis labels** (upright labels take far less width). Heatmaps and contingency tables
  already do this by default.
- **Shrink the tick-label font** with its slider.
- **Make the figure bigger** with **Plot Size**, or change its **Aspect** to give the labels room.
- **Shorten long names** — either turn on **Trim long labels** (on heatmaps), rename the columns
  first (see {doc}`organizing-data`), or number the categories and read the key beneath the figure.

```{tip}
Nothing you change here affects your data or your numbers — only how the figure is drawn. If you
make a mess, the reset button on a setting puts it back to its default.
```

Adjust the figure until it looks right, then copy or export it (see {doc}`exporting-results`).
