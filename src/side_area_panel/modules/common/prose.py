#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.


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
