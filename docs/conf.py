#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Sphinx configuration for the StatPrism user guide.

Authored in Markdown (via MyST). Built to HTML for the web and to PDF/ePub on
Read the Docs. Keep prose in the .md files; this file is wiring only.
"""

import re
from pathlib import Path

# -- Project information ------------------------------------------------------
project = "StatPrism"
author = "StatPrism Team"
copyright = "2026, StatPrism Team"


def _read_version() -> str:
    """Single source of truth: the version string in src/about.py. Parsed (not imported)
    so building the docs needs no app dependencies. Falls back to a placeholder."""
    about = Path(__file__).resolve().parent.parent / "src" / "about.py"
    try:
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', about.read_text(encoding="utf-8"))
        if match:
            return match.group(1)
    except OSError:
        pass
    return "0.0.0"


release = _read_version()  # full version, e.g. "1.0.2"
version = ".".join(release.split(".")[:2])  # short X.Y, e.g. "1.0"

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

# Expose the version to Markdown so prose can use {{ release }} instead of hardcoding it.
myst_substitutions = {
    "release": release,
    "version": version,
}

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
