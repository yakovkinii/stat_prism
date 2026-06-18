#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum


class RegressionModelType(Enum):
    LINEAR = "Linear (OLS)"
    LOGISTIC = "Logistic (binary)"

    @staticmethod
    def get_values():
        return [e.value for e in RegressionModelType]
