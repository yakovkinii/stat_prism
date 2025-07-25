#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum


class Languages(Enum):
    EN = "en"
    UA = "ua"


class Language:
    def __init__(self, language: Languages = Languages.EN):
        self.language = language

    def set_language(self, language: Languages):
        self.language = language

    def is_en(self):
        return self.language == Languages.EN

    def is_ua(self):
        return self.language == Languages.UA


LANGUAGE = Language()
