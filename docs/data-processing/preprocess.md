# Preprocess

A **batch** column set-up step: configure several columns at once — for each, recode values,
set its **type** (Nominal / Ordinal / Numeric) with an ordinal **order**, **rename** it, give
it a **color tag**, or mark it for **removal**. Think of it as doing many
{doc}`transform` edits in one place; handy right after import to tidy a whole dataset. (It
won't remove every column — at least one is always kept.)

Each column card has a **keep** checkbox (first), then the column **name** — click it to rename
in place (press **Tab** in the empty field to fill in the original name), a **color** swatch, a
copy-from-above button and a reset button. Below sit **Map values...** and the **type** dropdown
side by side, with an **Order...** button (ordinal columns only). The Map values and Order
buttons are highlighted when a mapping or a custom order is in effect; each of their pop-ups has a
**Reset** button to clear it.
