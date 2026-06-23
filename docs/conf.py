#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Sphinx configuration for the StatPrism user guide.

Authored in Markdown (via MyST). Built to HTML for the web and to PDF/ePub on
Read the Docs. Keep prose in the .md files; this file is wiring only.
"""

# -- Project information ------------------------------------------------------
project = "StatPrism"
author = "StatPrism Team"
copyright = "2026, StatPrism Team"

# Keep in step with src/about.py on each release.
release = "0.10.0"
version = "0.10"

# -- General configuration ----------------------------------------------------
extensions = [
    "myst_parser",
    "sphinx_copybutton",
]

# MyST Markdown extensions used across the guide.
myst_enable_extensions = [
    "colon_fence",   # ::: fenced admonitions / directives
    "deflist",       # definition lists
    "attrs_inline",  # inline attributes
    "linkify",       # bare URLs become links
    "tasklist",      # - [ ] checklists
    "substitution",
]
myst_heading_anchors = 3  # auto-anchor h1..h3 for cross-page links

source_suffix = {".md": "markdown", ".rst": "restructuredtext"}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "en"

# -- HTML output --------------------------------------------------------------
html_theme = "furo"
html_title = "StatPrism User Guide"
html_static_path = ["_static"]

html_theme_options = {
    "sidebar_hide_name": False,
}

# -- PDF (LaTeX) output -------------------------------------------------------
latex_elements = {
    "papersize": "a4paper",
    "pointsize": "11pt",
}
latex_documents = [
    ("index", "StatPrism.tex", "StatPrism User Guide", author, "manual"),
]
