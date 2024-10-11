from src.common.utility import smart_comma_join


def describe_test(
    test_name: str,
    accepted_columns: list[str],
    rejected_columns: list[str],
    accepted_property: str,
    rejected_property: str,
):
    if len(rejected_columns) == 0:
        return "The " + test_name + " has shown that all variables " + accepted_property + "."
    if len(accepted_columns) == 0:
        return "The " + test_name + " has shown that no variables " + accepted_property + "."

    text = ""
    if len(accepted_columns) == 1:
        text += (
            "The " + test_name + " has shown that the variable " + accepted_columns[0] + " " + accepted_property + ". "
        )
    else:
        text += (
            "The "
            + test_name
            + " has shown that the variables "
            + smart_comma_join(accepted_columns)
            + " "
            + accepted_property
            + ". "
        )

    if len(rejected_columns) == 1:
        text += "The variable " + rejected_columns[0] + " is " + rejected_property + "."
    else:
        text += "The variables " + smart_comma_join(rejected_columns) + " " + rejected_property + "."

    return text
