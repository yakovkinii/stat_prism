# Adjusting figures

Every figure in StatPrism is adjustable; the default appearance can be changed. This guide
shows where the controls are and how to correct the most common problem: text that overlaps.

## Where the settings are

Click a **figure** (or select its tab on a result card). Its **settings** appear in the panel on
the right. There is no code; the controls are sliders, dropdowns, checkboxes, and color pickers.
Each change redraws the figure immediately.

## What you can change

The exact controls depend on the figure, but you will usually find:

- **Colors**: line, bar, and point colors, the frame/text color, and the background.
- **Font sizes**: separate sliders for the title, axis titles, tick labels, and legend.
- **Axis titles and labels**: type your own axis titles; rotate the x-axis labels; number the
  categories instead of naming them.
- **Line thickness, point size, transparency**: for scatter/line/box plots.
- **Overall size and shape**: a **Plot Size** slider (bigger for a report, smaller to fit) and an
  **Aspect** slider (taller vs. wider).
- **Gridlines, frame, margins** and more.

## Fixing overlapping or cut-off text

If labels overlap or run off the edge – usually because you have many columns or long column names – 
this can usually be corrected by adjusting one or two settings:

- **Rotate the x-axis labels** (upright labels take far less width). Heatmaps and contingency tables
  already do this by default.
- **Shrink the tick-label font** with its slider.
- **Make the figure bigger** with **Plot Size**, or change its **Aspect** to give the labels room.
- **Shorten long names**: either turn on **Trim long labels** (on heatmaps), rename the columns
  first (see {doc}`organizing-data`), or number the categories and read the key beneath the figure.

```{tip}
Nothing you change here affects your data or your numbers, only how the figure is drawn. Each
setting has a reset button that restores its default.
```

Adjust the figure until it looks right, then copy or export it (see {doc}`exporting-results`).
