---
orphan: true
---

# Building the docs

The StatPrism user guide is built with **Sphinx** + **MyST** (Markdown). It is hosted on
**Read the Docs**, which rebuilds automatically on every push and produces the web, **PDF**,
and ePub versions (see `.readthedocs.yaml` at the repo root).

## Edit

Content lives in `docs/*.md` and `docs/analyses/*.md`. This is a **text-only** guide (no
screenshots). Add new pages to the relevant `toctree` in `index.md` (or `analyses/index.md`).

## Build locally (optional)

```
pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
```

Open `docs/_build/html/index.html`. To preview the PDF build you also need a LaTeX
toolchain; on Read the Docs this is handled for you.

## Versions & languages

- Read the Docs maps git branches/tags to documentation versions.
- The guide is English first; a Ukrainian translation can be added later via Sphinx's
  gettext workflow as a separate RTD language.
