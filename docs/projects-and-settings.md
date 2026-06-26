# Projects & settings

## Saving and reopening your work

A StatPrism **project** (`.sp` file) stores everything — the imported data, every
processing step, and every analysis with its settings and results.

- **File ▸ Save** — save to the current project file.
- **File ▸ Save As…** — save to a new file.
- **File ▸ Open…** — open a `.sp` project (or import a raw data file; see
  {doc}`importing-data`).

```{tip}
After you **Open** a `.sp` project, **Save** writes back to that same file — so once a
project is open, *Save* (not *Save As*) is the quick way to keep it up to date.
```

Project files are independent of the application folder, so they are safe across app
updates and easy to back up or share.

All preferences live under the **Settings** menu.

## Language

**Settings ▸ Language** switches the whole interface and all results between **English** and
**Ukrainian**. Switching re-renders existing results in the new language, so copy/export
*after* choosing the language you want.

## Plot theme

**Settings ▸ Plot theme** offers several looks for figures (for example *Default*, *Strict*,
and *Dark*). Changing it rebuilds plots and results with the new look. (Changing the theme
returns you to the home view, since results are regenerated.) Your choice is remembered
between sessions.

## UI theme

**Settings ▸ UI theme** switches the application's own appearance between **Light** and
**Dark**. This affects only the window chrome, not your results; it takes effect the next
time you start StatPrism.

## Auto-recalculate

**Settings ▸ Auto-recalculate**, when enabled, recomputes results automatically as you change
data steps. With it off, changed results are marked as needing recalculation and you refresh
them yourself (or use **File ▸ Recalculate All**, or press **Ctrl+R**). The setting is
remembered between sessions.

## Help / About

The **Help** menu includes the **User Guide** (this documentation) and **About**, with
version and project information.
