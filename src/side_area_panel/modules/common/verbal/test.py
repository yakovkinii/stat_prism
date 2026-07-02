#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import List, Union

from src.common.translations import t
from src.side_area_panel.modules.common.prose import ProseDetail, prose_detail_from
from src.side_area_panel.modules.common.utility import format_p_apa, format_statistic_apa, smart_comma_join


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
    ):
        self.variable = variable
        self.letter = letter
        self.statistic = statistic
        self.p = p
        self.df = df
        self.df2 = df2
        self.decimals = decimals

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


def describe_grouped_test(prose_detail, yes_columns, no_columns, *, test_name, test_check, yes_property, no_property):
    """Detail-aware wrapper over ``describe_single_test_multiple_variables`` for the shared
    "significant in which variables?" report. ``yes_columns`` are the significant results and
    ``no_columns`` the non-significant ones. At *Full* both are described; at *Significant only*
    / *Key findings* only the significant ones are (these tests have no separate notability
    notion). Returns None when there is nothing to say (so the caller can skip ``add_text``)."""
    detail = prose_detail_from(prose_detail)
    if detail == ProseDetail.NONE:
        return None
    included_no = no_columns if detail == ProseDetail.FULL else []
    if not yes_columns and not included_no:
        return None
    return describe_single_test_multiple_variables(
        test_name=test_name,
        test_check=test_check,
        yes_columns=yes_columns,
        no_columns=included_no,
        yes_property=yes_property,
        no_property=no_property,
    )
