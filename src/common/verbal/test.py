#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#
from typing import Dict, List, Union

from src.common.utility import format_p_apa, format_statistic_apa, format_value_apa, smart_comma_join


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
    subgroup_results: Dict[str, List[TestResult]] = None,
):
    text = "<div class='meta'>[Compact description]</div>" if subgroup_results is not None else ""
    text += f"""The {test_name} was used to check the {test_check} and has shown that """

    def _wrap_with_parentheses(x):
        return f" ({x})" if str(x) != "" else ""

    # If all variables have the same property, return a simple message
    suffix = ""
    if len(yes_columns) != 0:
        text += (
            smart_comma_join([f"{result.variable}{_wrap_with_parentheses(result)}" for result in yes_columns])
            + f" {yes_property}."
        )
        suffix = " On the other hand, "

    if len(no_columns) != 0:
        text += (
            suffix
            + smart_comma_join([f"{result.variable}{_wrap_with_parentheses(result)}" for result in no_columns])
            + f" {no_property}."
        )

    suffix = f"""The {test_name} was used to check the {test_check} and has shown that """
    if subgroup_results is not None:
        text += "<br><br><div class='meta'>[Detailed description]</div>"
        for result in yes_columns:
            suffix = ""
            text += f"The {test_name} has shown that {result.variable} {yes_property}{_wrap_with_parentheses(result)}. "
            for subgroup_result in subgroup_results[result.variable]:
                text += f"For the group {subgroup_result.variable}, {subgroup_result}. "

        if len(no_columns) != 0:
            text += (
                suffix
                + smart_comma_join([f"{result.variable}{_wrap_with_parentheses(result)}" for result in no_columns])
                + f" {no_property}."
            )
    return text


class NonTestResult:
    def __init__(self, variable: str, letters: List[str], values: List[float]):
        self.variable = variable
        self.letters = letters
        self.values = values

    def __str__(self):
        text = []
        for letter, value in zip(self.letters, self.values):
            text.append(f"{letter} = {format_value_apa(value)}")
        return ", ".join(text)


def describe_single_non_test_multiple_variables(
    statistic_name: str,
    columns: list[NonTestResult],
):
    text = f"""The {statistic_name} are """
    text += smart_comma_join([f"{result} for {result.variable}" for result in columns]) + f"."
    return text
