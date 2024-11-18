#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

from enum import Enum
from typing import Callable, List

import attrs


class DebtType(Enum):
    ON_STUDY_CHANGE = 0


@attrs.define
class Debt:
    debt_type: List[DebtType]
    resolve: Callable


DEBTS: List[Debt] = []
