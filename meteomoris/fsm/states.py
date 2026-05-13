from enum import Enum, auto


class State(Enum):
    IDLE = auto()
    CACHE_CHECK = auto()
    CACHE_HIT = auto()
    CACHE_MISS = auto()
    INTERNET_CHECK = auto()
    NO_INTERNET = auto()
    FETCHING = auto()
    FETCH_FAILED = auto()
    PARSING = auto()
    PARSE_FAILED = auto()
    CACHING = auto()
    DATA_READY = auto()
    RENDERING = auto()
    RETURNING = auto()
    COMPLETED = auto()
    ERROR = auto()


class Event(Enum):
    REQUEST = auto()
    CACHE_HIT = auto()
    CACHE_MISS = auto()
    INTERNET_OK = auto()
    NO_INTERNET = auto()
    FETCHED = auto()
    FETCH_FAILED = auto()
    PARSED = auto()
    PARSE_FAILED = auto()
    CACHED = auto()
    DATA_READY = auto()
    RENDER = auto()
    RENDERED = auto()
    RETURN = auto()
    ERROR_HANDLED = auto()
