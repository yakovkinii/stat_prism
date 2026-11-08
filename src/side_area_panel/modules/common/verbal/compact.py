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

"""Shared verbal-report compacter.

Every analysis maps its results into a list of :class:`ReportItem` and hands them, with its domain
nouns, to :func:`summarize`. The compacter decides the *structure* (which full-sentence template to
use) so the grammar stays correct per language, and aggregates results into summary sentences
instead of one identical sentence per item. The chosen :class:`~...prose.ProseDetail` level controls
depth:

* ``HEADLINE``     -- one sentence: the single most notable (else strongest significant) result;
* ``KEY``         -- the notable subset (a few outstanding results);
* ``SIGNIFICANT`` -- every significant result, compacted;
* ``FULL``        -- the above plus the non-significant results.

The APA statistics strings (``ReportItem.apa``) are passed through verbatim and always shown in full
for every named result -- the compacter never shortens them.
"""

from dataclasses import dataclass

from src.common.translations import t
from src.side_area_panel.modules.common.prose import ProseDetail, prose_detail_from
from src.side_area_panel.modules.common.utility import smart_comma_join

# How many non-significant results still read as "all ... except X, Y".
_EXCEPT_MAX = 2
# Up to this many significant results are listed individually rather than summarised as a count.
_FEW_MAX = 3
# How many outstanding results to name in a "the most notable were ..." clause.
_TOP_N = 3


@dataclass
class ReportItem:
    """One result feeding the compacter.

    ``label`` is the display name of the result (already escaped/quoted by the caller, e.g. an
    ``«A» & «B»`` pair or a predictor name). ``apa`` is the full APA statistics string, shown
    verbatim. ``magnitude`` ranks notability (larger = more outstanding). ``notable`` marks the
    "key finding" subset (e.g. a strong/large effect). ``descriptor`` is an optional short qualifier
    such as ``"strong, positive"``."""

    label: str
    significant: bool
    apa: str
    magnitude: float = 0.0
    notable: bool = False
    descriptor: str = ""


def _render(item: ReportItem) -> str:
    if item.descriptor:
        return t("verbal.compact.item_desc", label=item.label, desc=item.descriptor, apa=item.apa)
    return t("verbal.compact.item_plain", label=item.label, apa=item.apa)


def _render_many(items) -> str:
    return smart_comma_join([_render(it) for it in items])


def _top(items, limit=_TOP_N):
    """The most outstanding results, by descending magnitude."""
    return sorted(items, key=lambda it: it.magnitude, reverse=True)[:limit]


def _notable_clause(items, one_key, many_key) -> str:
    """ "The most notable ..." tail naming the outstanding results (drops when there are none).

    ``one_key`` / ``many_key`` are the singular/plural template keys; a module passes its own so the
    clause reads naturally for its domain (e.g. correlation: "the strongest correlation was ...")."""
    top = _top(items)
    if not top:
        return ""
    if len(top) == 1:
        return t(one_key, items=_render(top[0]))
    return t(many_key, items=_render_many(top))


def summarize(
    items,
    detail,
    *,
    noun_nom,
    noun_gen,
    notable_one_key="verbal.compact.most_notable_one",
    notable_key="verbal.compact.most_notable",
) -> str:
    """Compacted findings prose for ``items`` at the chosen ``detail`` level.

    ``noun_nom`` / ``noun_gen`` are the already-translated nominative and genitive plural forms of
    the domain noun (e.g. "correlations" / "коефіцієнтів кореляції"); templates pick the form they
    need so the grammar stays correct. ``notable_one_key`` / ``notable_key`` let a module supply its
    own "the most notable ..." phrasing. Returns ``""`` when there is nothing to say at this level.
    """
    level = prose_detail_from(detail)
    if level == ProseDetail.NONE or not items:
        return ""

    n = len(items)
    sig = [it for it in items if it.significant]
    nonsig = [it for it in items if not it.significant]
    notable = [it for it in sig if it.notable]
    k = len(sig)

    # HEADLINE: a single sentence naming the one standout result (notable first, else strongest
    # significant); if nothing is significant, say so.
    if level == ProseDetail.HEADLINE:
        pool = notable or sig
        if not pool:
            return t("verbal.compact.none", noun=noun_gen)
        return t(notable_one_key, items=_render(_top(pool, 1)[0]))

    # KEY: the outstanding (notable) subset only.
    if level == ProseDetail.KEY:
        if not notable:
            return t("verbal.compact.key_none_notable", noun=noun_gen)
        return _notable_clause(notable, notable_one_key, notable_key)

    # SIGNIFICANT / FULL share the significant-results summary; FULL then appends the rest.
    text = _significant_summary(sig, nonsig, notable, n, k, noun_nom, noun_gen, notable_one_key, notable_key)
    if level == ProseDetail.FULL and nonsig and k != 0 and k != n:
        text += t("verbal.compact.remaining_nonsig", noun=noun_gen, items=_render_many(nonsig))
    return text


def _significant_summary(sig, nonsig, notable, n, k, noun_nom, noun_gen, notable_one_key, notable_key) -> str:
    """The compacted summary of which results were significant (used by SIGNIFICANT and FULL)."""
    if k == 0:
        return t("verbal.compact.none", noun=noun_gen)

    def notable_clause():
        return _notable_clause(notable or sig, notable_one_key, notable_key)

    if k == n:
        return t("verbal.compact.all", noun=noun_nom) + notable_clause()

    # All but a couple -> "all ... except X, Y" (only when the significant ones are the majority).
    if len(nonsig) <= _EXCEPT_MAX and k > n / 2:
        exceptions = smart_comma_join([it.label for it in nonsig])
        return t("verbal.compact.all_except", noun=noun_nom, exceptions=exceptions) + notable_clause()

    # Few significant -> list them individually (APA in full), no separate "most notable" tail.
    if k <= _FEW_MAX:
        key = "verbal.compact.few_one" if k == 1 else "verbal.compact.few"
        return t(key, k=k, n=n, noun=noun_gen, items=_render_many(_top(sig, _FEW_MAX)))

    # Many significant -> a count summary ("most" only when it is a majority) + the outstanding few.
    head_key = "verbal.compact.most" if k > n / 2 else "verbal.compact.minority"
    return t(head_key, k=k, n=n, noun=noun_gen) + notable_clause()
