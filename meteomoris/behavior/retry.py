import time
import requests


class RetryPolicy:
    def __init__(self, max_retries=3, base_delay=1.0, max_delay=30.0,
                 backoff_factor=2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor

    def should_retry(self, attempt, exception):
        if attempt >= self.max_retries:
            return False
        if isinstance(exception, requests.Timeout):
            return True
        if isinstance(exception, requests.ConnectionError):
            return True
        if isinstance(exception, requests.HTTPError):
            status = exception.response.status_code
            return 500 <= status < 600
        return False

    def is_retryable_exception(self, exception):
        return self.should_retry(0, exception)

    def delay(self, attempt):
        return min(self.base_delay * (self.backoff_factor ** attempt),
                   self.max_delay)

    def sleep(self, attempt):
        time.sleep(self.delay(attempt))

    def classify_exception(self, exception):
        if isinstance(exception, requests.Timeout):
            return "timeout"
        if isinstance(exception, requests.ConnectionError):
            return "network"
        if isinstance(exception, requests.HTTPError):
            status = exception.response.status_code
            if 400 <= status < 500:
                return "http_4xx"
            if 500 <= status < 600:
                return "http_5xx"
        return "unknown"
