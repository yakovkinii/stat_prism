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


from typing import List, Union

from src.common.translations import t
from src.side_area_panel.modules.common.prose import ProseDetail, prose_detail_from
from src.side_area_panel.modules.common.utility import format_p_apa, format_statistic_apa, smart_comma_join
from src.side_area_panel.modules.common.verbal.compact import ReportItem, summarize


class TestResult:
    def __init__(
        self,
        variable: str,
        letter: Union[str, List[str]],
        statistic: Union[Union[float, str], List[Union[float, str]]],
        p: Union[float, str] = None,
        df: Union[int, str] = None,
        df2: Union[int, str] = None,
        decimals: int = 2,
        effect: float = None,
        effect_word: str = "",
    ):
        self.variable = variable
        self.letter = letter
        self.statistic = statistic
        self.p = p
        self.df = df
        self.df2 = df2
        self.decimals = decimals
        # Optional effect size + its magnitude word, used by the verbal compacter to rank the
        # outstanding results and to label them (e.g. "large"); absent -> ranked by |statistic|.
        self.effect = effect
        self.effect_word = effect_word

    def _magnitude(self) -> float:
        source = (
            self.effect
            if self.effect is not None
            else (self.statistic[0] if isinstance(self.statistic, list) else self.statistic)
        )
        try:
            value = abs(float(source))
        except (TypeError, ValueError):
            return 0.0
        return value if value == value else 0.0  # NaN -> 0

    def __str__(self):
        if isinstance(self.letter, list):
            text = []
            for i, (letter, stat) in enumerate(zip(self.letter, self.statistic)):
                if i == 0:
                    snippet = ""
                    if self.df2 is not None:
                        snippet += f"{letter}({self.df}, {self.df2}) = {format_statistic_apa(stat, self.decimals)}"
                    elif self.df is not None:
                        snippet += f"{letter}({self.df}) = {format_statistic_apa(stat,self.decimals)}"
                    else:
                        snippet += f"{letter} = {format_statistic_apa(stat,self.decimals)}"
                    if self.p is not None:
                        snippet += f", p {format_p_apa(self.p, add_equals=True)}"
                    text.append(snippet)
                else:
                    text.append(f"{letter} = {format_statistic_apa(stat,self.decimals)}")

            return ", ".join(text)
        else:
            if self.df2 is not None:
                text = f"{self.letter}({self.df}, {self.df2}) = {format_statistic_apa(self.statistic,self.decimals)}"
            elif self.df is not None:
                text = f"{self.letter}({self.df}) = {format_statistic_apa(self.statistic,self.decimals)}"
            else:
                text = f"{self.letter} = {format_statistic_apa(self.statistic,self.decimals)}"
            if self.p is not None:
                text += f", p {format_p_apa(self.p, add_equals=True)}"
        return text


def describe_single_test_multiple_variables(
    test_name: str,
    test_check: str,
    yes_columns: list[TestResult],
    no_columns: list[TestResult],
    yes_property: str,
    no_property: str,
):
    # Single report (the previous compact + detailed duality was removed).
    text = t("ttest.verbal.used_to_check", test_name=test_name, test_check=test_check)

    def _wrap_with_parentheses(x):
        return f" ({x})" if str(x) != "" else ""

    suffix = ""
    if len(yes_columns) != 0:
        text += (
            smart_comma_join([f"{result.variable}{_wrap_with_parentheses(result)}" for result in yes_columns])
            + f" {yes_property}."
        )
        suffix = t("ttest.verbal.on_other_hand")

    if len(no_columns) != 0:
        text += (
            suffix
            + smart_comma_join([f"{result.variable}{_wrap_with_parentheses(result)}" for result in no_columns])
            + f" {no_property}."
        )

    return text


def describe_grouped_test(
    prose_detail,
    yes_columns,
    no_columns,
    *,
    noun_nom,
    noun_gen,
    notable_one_key,
    notable_key,
):
    """Compacted verbal summary of a test applied to several variables, via the shared compacter.

    ``yes_columns`` are the significant :class:`TestResult`s, ``no_columns`` the non-significant
    ones. The result groups them ("all ... except X", "most ...", "the largest difference was ...")
    instead of one sentence per variable, with full APA stats, at the chosen prose level.
    """
    detail = prose_detail_from(prose_detail)
    if detail == ProseDetail.NONE:
        return None

    def to_item(test_result, significant):
        return ReportItem(
            label=f"&laquo;{test_result.variable}&raquo;",
            significant=significant,
            apa=str(test_result),
            magnitude=test_result._magnitude(),
            notable=significant,
            descriptor=test_result.effect_word or "",
        )

    items = [to_item(tr, True) for tr in yes_columns] + [to_item(tr, False) for tr in no_columns]
    if not items:
        return None
    text = summarize(
        items,
        detail,
        noun_nom=noun_nom,
        noun_gen=noun_gen,
        notable_one_key=notable_one_key,
        notable_key=notable_key,
    )
    return text or None
