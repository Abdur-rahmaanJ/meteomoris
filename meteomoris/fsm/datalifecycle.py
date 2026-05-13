import time
import datetime
import traceback

from ..behavior.auditor import Auditor
from ..behavior.retry import RetryPolicy
from ..model.entities import Result
from ..model.error import ErrorRecord, ErrorType
from .states import State, Event


class DataLifecycleFSM:
    TRANSITIONS = {
        (State.IDLE, Event.REQUEST): (State.CACHE_CHECK, None),
        (State.CACHE_CHECK, Event.CACHE_HIT): (State.CACHE_HIT, None),
        (State.CACHE_CHECK, Event.CACHE_MISS): (State.CACHE_MISS, None),
        (State.CACHE_HIT, Event.DATA_READY): (State.DATA_READY, None),
        (State.CACHE_MISS, Event.INTERNET_OK): (State.FETCHING, None),
        (State.CACHE_MISS, Event.NO_INTERNET): (State.NO_INTERNET, None),
        (State.FETCHING, Event.FETCHED): (State.PARSING, None),
        (State.FETCHING, Event.FETCH_FAILED): (State.ERROR, None),
        (State.PARSING, Event.PARSED): (State.CACHING, None),
        (State.PARSING, Event.PARSE_FAILED): (State.ERROR, None),
        (State.CACHING, Event.CACHED): (State.DATA_READY, None),
        (State.CACHING, Event.CACHE_FAILED): (State.DATA_READY, None),
        (State.NO_INTERNET, Event.ABORT): (State.ABORTED, None),
        (State.NO_INTERNET, Event.DEGRADE): (State.STALE_CACHE_CHECK, None),
        (State.DATA_READY, Event.RENDER): (State.RENDERING, None),
        (State.DATA_READY, Event.RETURN): (State.RETURNING, None),
        (State.RENDERING, Event.RENDERED): (State.RETURNING, None),
        (State.RETURNING, Event.RETURN): (State.COMPLETED, None),
        (State.ERROR, Event.RETURN): (State.COMPLETED, None),
        (State.STALE_CACHE_CHECK, Event.STALE_FOUND): (State.STALE_CACHE, None),
        (State.STALE_CACHE_CHECK, Event.STALE_NOT_FOUND): (State.ERROR, None),
        (State.STALE_CACHE, Event.DATA_READY): (State.DATA_READY, None),
        (State.ABORTED, Event.RETURN): (State.COMPLETED, None),
    }

    def __init__(self, source_spec, cache, fetcher, parser, renderer,
                 auditor=None, retry_policy=None):
        self.state = State.IDLE
        self.source = source_spec
        self.cache = cache
        self.fetcher = fetcher
        self.parser = parser
        self.renderer = renderer
        self.auditor = auditor or Auditor()
        self.retry_policy = retry_policy or RetryPolicy()
        self.data = None
        self.html = None
        self.error = None
        self._retry_attempt = 0
        self._result_errors = []

    def _get_next(self, event):
        return self.TRANSITIONS.get((self.state, event))

    def _transition(self, event):
        entry = self._get_next(event)
        if entry is None:
            raise RuntimeError(
                "Invalid transition: {} from {}".format(event, self.state)
            )
        self.state = entry[0]

    def _make_error_record(self, exception, attempt, error_type=None):
        if error_type is None:
            rp = self.retry_policy
            error_type = rp.classify_exception(exception)
            et_map = {
                "timeout": ErrorType.TIMEOUT,
                "network": ErrorType.NETWORK,
                "http_4xx": ErrorType.HTTP_4XX,
                "http_5xx": ErrorType.HTTP_5XX,
            }
            error_type = et_map.get(error_type, ErrorType.UNKNOWN)
        return ErrorRecord(
            timestamp=datetime.datetime.now(),
            source_id=self.source.get("cache_key", "unknown"),
            state=self.state,
            error_type=error_type,
            message=str(exception),
            is_retryable=self.retry_policy.is_retryable_exception(exception),
            attempt=attempt,
            exception=exception,
            traceback=traceback.format_exc(),
        )

    def _make_result(self, success):
        return Result(
            success=success,
            data=self.data,
            errors=self._result_errors,
            from_stale_cache=getattr(self, "_stale_served", False),
            error=self._result_errors[-1] if self._result_errors else None,
        )

    def execute(self, print_output=False, **params):
        try:
            self._transition(Event.REQUEST)

            if self.state == State.CACHE_CHECK:
                cached = self.cache.get(self.source["cache_key"])
                if cached is not None:
                    self.data = cached
                    self._transition(Event.CACHE_HIT)
                    self._transition(Event.DATA_READY)
                else:
                    self._transition(Event.CACHE_MISS)

            if self.state == State.CACHE_MISS:
                if self.source["requires_internet"]:
                    if not self.fetcher.check_internet():
                        self._transition(Event.NO_INTERNET)
                        return self._handle_no_internet()
                    self._transition(Event.INTERNET_OK)
                else:
                    self._transition(Event.INTERNET_OK)

            if self.state == State.FETCHING:
                fetch_success = self._attempt_fetch_with_retry()
                if not fetch_success:
                    return self._handle_fetch_failure()

            if self.state == State.PARSING:
                self.parser.auditor = self.auditor
                parser_method = getattr(
                    self.parser, self.source["parser"], None
                )
                if parser_method is None:
                    err = ErrorRecord(
                        timestamp=datetime.datetime.now(),
                        source_id=self.source.get("cache_key", "unknown"),
                        state=self.state,
                        error_type=ErrorType.PARSE,
                        message="Parser method '{}' not found".format(
                            self.source["parser"]
                        ),
                        is_retryable=False,
                        attempt=0,
                    )
                    self.auditor.record_error(err)
                    self._result_errors.append(err)
                    self._transition(Event.PARSE_FAILED)
                    return self._make_result(False)
                result = parser_method(self.html)
                if result is None:
                    err = ErrorRecord(
                        timestamp=datetime.datetime.now(),
                        source_id=self.source.get("cache_key", "unknown"),
                        state=self.state,
                        error_type=ErrorType.PARSE,
                        message="Parser returned no data",
                        is_retryable=False,
                        attempt=0,
                    )
                    self.auditor.record_error(err)
                    self._result_errors.append(err)
                    self._transition(Event.PARSE_FAILED)
                    return self._make_result(False)
                self.data = result
                self._transition(Event.PARSED)

            if self.state == State.CACHING:
                cache_key = self.source.get("cache_key")
                if cache_key and self.cache.enabled:
                    try:
                        self.cache.set(cache_key, self._data_to_cache())
                    except Exception as e:
                        self.auditor.record_error(ErrorRecord(
                            timestamp=datetime.datetime.now(),
                            source_id=self.source.get("cache_key", "unknown"),
                            state=self.state,
                            error_type=ErrorType.CACHE,
                            message=str(e),
                            is_retryable=False,
                            attempt=0,
                        ))
                self._transition(Event.CACHED)

            if self.state == State.DATA_READY and print_output:
                self._transition(Event.RENDER)

            if self.state == State.RENDERING:
                self._on_render(**params)
                self._transition(Event.RENDERED)

            if self.state in (State.RETURNING, State.COMPLETED):
                self._transition(Event.RETURN)
                return self._make_result(True)

            self._transition(Event.RETURN)
            if self.state == State.RETURNING:
                self._transition(Event.RETURN)
            return self._make_result(True)

        except Exception as e:
            self.error = e
            self.state = State.ERROR
            err = self._make_error_record(e, self._retry_attempt)
            self._result_errors.append(err)
            return self._make_result(False)

    def _attempt_fetch_with_retry(self):
        self._retry_attempt = 0
        while self._retry_attempt <= self.retry_policy.max_retries:
            try:
                response = self.fetcher.fetch(self.source["url"])
                if response is None:
                    raise RuntimeError("fetch returned no response")
                self.html = response.content
                self._transition(Event.FETCHED)
                return True
            except Exception as e:
                err = self._make_error_record(e, self._retry_attempt)
                self.auditor.record_error(err)
                self._result_errors.append(err)
                if self._retry_attempt < self.retry_policy.max_retries:
                    if self.retry_policy.should_retry(
                            self._retry_attempt, e):
                        delay = self.retry_policy.delay(self._retry_attempt)
                        self.state = State.RETRYING
                        time.sleep(delay)
                        self.state = State.FETCHING
                        self._retry_attempt += 1
                        continue
                self._transition(Event.FETCH_FAILED)
                return False
        self._transition(Event.FETCH_FAILED)
        return False

    def _handle_no_internet(self):
        err = ErrorRecord(
            timestamp=datetime.datetime.now(),
            source_id=self.source.get("cache_key", "unknown"),
            state=self.state,
            error_type=ErrorType.NO_INTERNET,
            message="No internet connection",
            is_retryable=True,
            attempt=0,
        )
        self.auditor.record_error(err)
        self._result_errors.append(err)
        self._transition(Event.DEGRADE)
        return self._handle_stale_cache_fallback()

    def _handle_fetch_failure(self):
        return self._handle_stale_cache_fallback()

    def _handle_stale_cache_fallback(self):
        cache_key = self.source.get("cache_key")
        if cache_key:
            stale = self.cache.get_stale(cache_key)
            if stale:
                self.data = stale
                self._stale_served = True
                self._transition(Event.DATA_READY)
                return self._make_result(True)
        return self._make_result(False)

    def _data_to_cache(self):
        if hasattr(self.data, "to_dict"):
            return self.data.to_dict()
        if isinstance(self.data, list):
            return [d.to_dict() if hasattr(d, "to_dict") else d
                    for d in self.data]
        if isinstance(self.data, dict):
            return {
                k: v.to_dict() if hasattr(v, "to_dict") else v
                for k, v in self.data.items()
            }
        return self.data

    RENDER_MAP = {
        "parse_sunrise_table": "render_sunrise",
        "parse_moonrise_table": "render_moonrise",
    }

    def _on_render(self, **params):
        render_name = self.RENDER_MAP.get(
            self.source["parser"],
            "render_" + self.source["parser"].replace("parse_", ""),
        )
        render_method = getattr(self.renderer, render_name, None)
        if render_method:
            render_data = self._data_to_cache()
            render_method(render_data, **params)

    def _on_return(self):
        pass

    def _on_error(self):
        pass

    def _on_error_return(self):
        pass
