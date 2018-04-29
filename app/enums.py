from enum import Enum


class FileCategory(Enum):
    UPLOADS = 1
    EXAMINATION = 2
    ACTIVITY_PICTURE = 3
    ALV_DOCUMENT = 4
    COMPANY_LOGO = 5
    USER_AVATAR = 6


class PimpyTaskStatus(Enum):
    NOT_STARTED = 0
    STARTED = 1
    DONE = 2
    NOT_DONE = 3
    CHECKED = 4
    DELETED = 5
    MAX = 5
