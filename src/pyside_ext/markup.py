#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#


def css(selector: str = "#id", **kwargs):
    properties = "\n".join(f"\t{key.replace('_', '-')}: {value};" for key, value in kwargs.items())
    return f"{selector}{{\n{properties}\n}}"


class HTML:
    @staticmethod
    def div(contents: str, **kwargs):
        style = "; ".join(f"{key.replace('_', '-')}: {value}" for key, value in kwargs.items())
        return f'<div style="{style}">{contents}</div>'

    @staticmethod
    def bold(contents: str):
        return f"<b>{contents}</b>"

    @staticmethod
    def hr():
        return "<hr>"
