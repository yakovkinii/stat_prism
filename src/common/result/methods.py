#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

from src.common.result.registry import RESULTS


def get_unique_result_id():
    return max(RESULTS.keys()) + 1 if len(RESULTS) > 0 else 1
