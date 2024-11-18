#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

from enum import Enum

import attrs


class MessageType(Enum):
    EDITING_FINISHED = 1
    STATE_CHANGED = 2
    CLICKED = 3
    FILTER_ADDED = 5
    FILTER_CLICKED = 6


@attrs.define
class Message:
    message_type: MessageType
    payload: any = None
    caller_id: any = None
