import enum

class UserRoleEnum(str, enum.Enum):
    USER = 'user'
    ADMIN = 'admin'
    AUTHOR = 'author'