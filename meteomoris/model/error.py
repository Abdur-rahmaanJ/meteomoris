import datetime
from enum import Enum, auto


class ErrorType(Enum):
    NETWORK = auto()
    HTTP_4XX = auto()
    HTTP_5XX = auto()
    TIMEOUT = auto()
    PARSE = auto()
    CACHE = auto()
    NO_INTERNET = auto()
    INTERNET_CHECK = auto()
    UNKNOWN = auto()


class ErrorRecord:
    def __init__(self, timestamp, source_id, state, error_type, message,
                 is_retryable, attempt, exception=None, traceback=None):
        self.timestamp = timestamp
        self.source_id = source_id
        self.state = state
        self.error_type = error_type
        self.message = message
        self.is_retryable = is_retryable
        self.attempt = attempt
        self.exception = exception
        self.traceback = traceback

    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "source_id": self.source_id,
            "state": str(self.state),
            "error_type": self.error_type.name,
            "message": self.message,
            "is_retryable": self.is_retryable,
            "attempt": self.attempt,
        }
