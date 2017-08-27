from enum import Enum, unique


@unique
class Roles(Enum):
    """
    Roles used to secure the application

    Note: When updating the list of roles, also insert them in the roles
    table.
    """
    ALV_WRITE = 'ALV_WRITE'
    ALV_READ = 'ALV_READ'
    ACTIVITY_WRITE = 'ACTIVITY_WRITE'
    ACTIVITY_READ = 'ACTIVITY_READ'
