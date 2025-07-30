
from enum import Enum


class MemoryType(Enum):
    INSERT_MEMORY = "insertMemory"
    SEARCH_MEMORY = "searchMemory"


class OutPutType(Enum):
    TEXT = "text"
    JSON = "json"


class HitStrategyType(Enum):
    MIX = 1
    KEY = 2
    SEMANTICS = 3