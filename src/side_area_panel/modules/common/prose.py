#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Shared "how much prose" control for the analysis modules.

Every module that writes a plain-language interpretation offers the *same* dropdown instead
of an on/off checkbox, so the amount of prose scales with how much there is to say:

    None            -- no prose at all (tables/plots only)
    Key findings    -- only the notable results (e.g. strong correlations, large effects)
    Significant     -- only the statistically significant results
    Full            -- every result, significant or not

Modules decide, per result, whether it is *significant* and (optionally) *notable*; the
``prose_includes`` helper then applies the chosen level uniformly. ``PROSE_LEVELS`` feeds the
``IISPWACComboBox`` in each settings panel and the value is stored verbatim in the config
(like the other combobox settings), so no translation table is needed for the labels.
"""

from enum import Enum


class ProseDetail(Enum):
    NONE = "None"
    KEY = "Key findings"
    SIGNIFICANT = "Significant only"
    FULL = "Full"

    @staticmethod
    def values():
        return [e.value for e in ProseDetail]


# Order shown in the dropdown (least -> most prose).
PROSE_LEVELS = ProseDetail.values()

# Label reused by every settings panel so the control reads the same everywhere.
PROSE_LABEL = "Verbal report:"


def prose_detail_from(value) -> ProseDetail:
    """Config value (string or already-a-ProseDetail) -> ProseDetail, defaulting to NONE."""
    if isinstance(value, ProseDetail):
        return value
    for level in ProseDetail:
        if level.value == value:
            return level
    return ProseDetail.NONE


def prose_enabled(detail) -> bool:
    """True when any prose should be written (the module can skip building it otherwise)."""
    return prose_detail_from(detail) != ProseDetail.NONE


def prose_includes(detail, significant: bool, notable: bool = False) -> bool:
    """Whether a single result should be mentioned at the chosen detail level.

    ``notable`` marks the "key finding" subset (e.g. a strong/large effect). Modules with no
    meaningful notability distinction should pass ``notable=significant`` so that *Key findings*
    degenerates to *Significant only* for them."""
    level = prose_detail_from(detail)
    if level == ProseDetail.FULL:
        return True
    if level == ProseDetail.SIGNIFICANT:
        return significant
    if level == ProseDetail.KEY:
        return notable
    return False
