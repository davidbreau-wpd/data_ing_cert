from enum import Enum, auto

class DatabaseType(Enum):
    Azure = auto()
    Local = auto() #SQLAlchemy