from enum import Enum


class PimpyTaskStatus(Enum):
    NOT_STARTED = 0
    STARTED = 1
    DONE = 2
    NOT_DONE = 3
    CHECKED = 4
    DELETED = 5
    MAX = 5
