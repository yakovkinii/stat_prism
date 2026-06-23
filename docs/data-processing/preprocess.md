# Preprocess

A **batch** column set-up step: configure several columns at once — for each, recode values,
set its **type** (Nominal / Ordinal / Numeric) with an ordinal **order**, **rename** it, give
it a **colour tag**, or mark it for **removal**. Think of it as doing many
{doc}`transform` edits in one place; handy right after import to tidy a whole dataset. (It
won't remove every column — at least one is always kept.)
