#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

from src.common.utility import smart_comma_join


def describe_test(
    test_name: str,
    yes_columns: list[str],
    no_columns: list[str],
    yes_property: str,
    no_property: str,
):
    if len(no_columns) == 0:
        return "The " + test_name + " has shown that all variables " + yes_property + "."
    if len(yes_columns) == 0:
        return "The " + test_name + " has shown that no variables " + yes_property + "."

    text = ""
    if len(yes_columns) == 1:
        text += "The " + test_name + " has shown that the variable " + yes_columns[0] + " " + yes_property + ". "
    else:
        text += (
            "The "
            + test_name
            + " has shown that the variables "
            + smart_comma_join(yes_columns)
            + " "
            + yes_property
            + ". "
        )

    if len(no_columns) == 1:
        text += "The variable " + no_columns[0] + " is " + no_property + "."
    else:
        text += "The variables " + smart_comma_join(no_columns) + " " + no_property + "."

    return text
