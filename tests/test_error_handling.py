import time
import json
import os
import requests
import datetime
from unittest.mock import patch

from meteomoris.fsm.states import State, Event
from meteomoris.fsm.datalifecycle import DataLifecycleFSM
from meteomoris.fsm.dispatch import FSMDispatch
from meteomoris.behavior.retry import RetryPolicy
from meteomoris.behavior.auditor import Auditor
from meteomoris.behavior.cache import Cache
from meteomoris.model.entities import Result
from meteomoris.model.error import ErrorRecord, ErrorType
from meteomoris.model.sources import DATASOURCES


class FakeCache:
    def __init__(self):
        self.enabled = True
        self._fresh = {}
        self._stale = {}

    def get(self, key):
        return self._fresh.get(key)

    def get_stale(self, key):
        return self._stale.get(key) or self._fresh.get(key)

    def set(self, key, data):
        self._fresh[key] = data


class FakeFetcher:
    def __init__(self, online=True, html="<html></html>"):
        self.online = online
        self.html = html
        self._call_count = 0

    def check_internet(self):
        return self.online

    def fetch(self, url, timeout=None):
        self._call_count += 1
        class FakeResponse:
            def __init__(self, content):
                self.content = content
                self.text = content if isinstance(content, str) else content.decode()
        return FakeResponse(self.html)


class FailingFetcher(FakeFetcher):
    def __init__(self, fail_times=2, online=True, html="<html></html>"):
        super().__init__(online=online, html=html)
        self.fail_times = fail_times
        self._call_count = 0

    def fetch(self, url, timeout=None):
        self._call_count += 1
        if self._call_count <= self.fail_times:
            raise requests.ConnectionError("Simulated failure")
        return super().fetch(url, timeout=None)


class FakeParser:
    def __init__(self):
        self.auditor = None

    def parse_weekforecast(self, html):
        return ["fake_forecast"]

    def parse_failing(self, html):
        return None


class FakeRenderer:
    def __init__(self):
        self.rendered = []

    def render_weekforecast(self, data, **kwargs):
        self.rendered.append(("weekforecast", data, kwargs))


def make_fsm(source_id, cache=None, fetcher=None, parser=None,
             renderer=None, auditor=None, retry_policy=None):
    source = dict(DATASOURCES[source_id])
    return DataLifecycleFSM(
        source,
        cache or FakeCache(),
        fetcher or FakeFetcher(),
        parser or FakeParser(),
        renderer or FakeRenderer(),
        auditor=auditor or Auditor(),
        retry_policy=retry_policy or RetryPolicy(max_retries=0),
    )


class TestRetryPolicy:
    def test_exponential_backoff_delays(self):
        policy = RetryPolicy(max_retries=3, base_delay=1.0, backoff_factor=2.0)
        assert policy.delay(0) == 1.0
        assert policy.delay(1) == 2.0
        assert policy.delay(2) == 4.0

    def test_delay_capped(self):
        policy = RetryPolicy(max_retries=10, base_delay=1.0, max_delay=10.0,
                              backoff_factor=3.0)
        assert policy.delay(0) == 1.0
        assert policy.delay(1) == 3.0
        assert policy.delay(2) == 9.0
        assert policy.delay(3) == 10.0
        assert policy.delay(10) == 10.0

    def test_should_retry_within_limit(self):
        policy = RetryPolicy(max_retries=3)
        assert policy.should_retry(0, requests.ConnectionError())
        assert policy.should_retry(1, requests.ConnectionError())
        assert policy.should_retry(2, requests.ConnectionError())
        assert not policy.should_retry(3, requests.ConnectionError())

    def test_http_5xx_is_retryable(self):
        policy = RetryPolicy(max_retries=3)
        resp = requests.Response()
        resp.status_code = 500
        assert policy.should_retry(0, requests.HTTPError(response=resp))

    def test_http_4xx_not_retryable(self):
        policy = RetryPolicy(max_retries=3)
        resp = requests.Response()
        resp.status_code = 404
        assert not policy.should_retry(0, requests.HTTPError(response=resp))

    def test_timeout_is_retryable(self):
        policy = RetryPolicy(max_retries=3)
        assert policy.should_retry(0, requests.Timeout())

    def test_classify_exception(self):
        policy = RetryPolicy()
        assert policy.classify_exception(requests.Timeout()) == "timeout"
        assert policy.classify_exception(requests.ConnectionError()) == "network"
        resp = requests.Response()
        resp.status_code = 500
        assert policy.classify_exception(
            requests.HTTPError(response=resp)) == "http_5xx"
        resp.status_code = 404
        assert policy.classify_exception(
            requests.HTTPError(response=resp)) == "http_4xx"
        assert policy.classify_exception(ValueError()) == "unknown"


class TestFSMRetry:
    def test_retry_succeeds_after_failures(self):
        cache = FakeCache()
        fetcher = FailingFetcher(fail_times=2)
        fsm = make_fsm("weekforecast", cache=cache, fetcher=fetcher,
                        retry_policy=RetryPolicy(max_retries=3))
        result = fsm.execute(print_output=False)
        assert result.success
        assert result.data == ["fake_forecast"]

    def test_retry_exhausted_returns_failure(self):
        cache = FakeCache()
        fetcher = FailingFetcher(fail_times=5)
        fsm = make_fsm("weekforecast", cache=cache, fetcher=fetcher,
                        retry_policy=RetryPolicy(max_retries=2))
        result = fsm.execute(print_output=False)
        assert not result.success

    def test_retry_has_audit_errors(self):
        cache = FakeCache()
        fetcher = FailingFetcher(fail_times=1)
        auditor = Auditor()
        fsm = make_fsm("weekforecast", cache=cache, fetcher=fetcher,
                        auditor=auditor,
                        retry_policy=RetryPolicy(max_retries=3))
        fsm.execute(print_output=False)
        errors = auditor.get_errors(source_id="weekforecast")
        assert len(errors) >= 1


class TestStaleCache:
    def test_stale_cache_served_on_fetch_failure(self):
        cache = FakeCache()
        cache._stale["weekforecast"] = ["stale_data"]
        class OfflineFetcher(FakeFetcher):
            def check_internet(self):
                return True
            def fetch(self, url, timeout=None):
                return None
        fsm = make_fsm("weekforecast", cache=cache, fetcher=OfflineFetcher(),
                        retry_policy=RetryPolicy(max_retries=1))
        result = fsm.execute(print_output=False)
        assert result.success
        assert result.data == ["stale_data"]
        assert result.from_stale_cache

    def test_no_stale_cache_returns_failure(self):
        cache = FakeCache()
        class OfflineFetcher(FakeFetcher):
            def check_internet(self):
                return True
            def fetch(self, url, timeout=None):
                return None
        fsm = make_fsm("weekforecast", cache=cache, fetcher=OfflineFetcher(),
                        retry_policy=RetryPolicy(max_retries=1))
        result = fsm.execute(print_output=False)
        assert not result.success


class TestNoInternet:
    def test_no_internet_graceful_degradation(self):
        cache = FakeCache()
        class OfflineFetcher(FakeFetcher):
            def check_internet(self):
                return False
        fsm = make_fsm("weekforecast", cache=cache, fetcher=OfflineFetcher())
        result = fsm.execute(print_output=False)
        assert not result.success

    def test_no_internet_returns_stale_cache(self):
        cache = FakeCache()
        cache._stale["weekforecast"] = ["stale_from_no_internet"]
        class OfflineFetcher(FakeFetcher):
            def check_internet(self):
                return False
        fsm = make_fsm("weekforecast", cache=cache, fetcher=OfflineFetcher())
        result = fsm.execute(print_output=False)
        assert result.success
        assert result.from_stale_cache


class TestAuditor:
    def test_auditor_records_error(self):
        auditor = Auditor()
        auditor.record_error(ErrorRecord(
            timestamp=datetime.datetime.now(),
            source_id="test",
            state=State.ERROR,
            error_type=ErrorType.NETWORK,
            message="test error",
            is_retryable=True,
            attempt=0,
        ))
        errors = auditor.get_errors()
        assert len(errors) == 1
        assert errors[0].source_id == "test"

    def test_auditor_filter_by_source(self):
        auditor = Auditor()
        for src in ["a", "b", "a"]:
            auditor.record_error(ErrorRecord(
                timestamp=datetime.datetime.now(),
                source_id=src, state=None, error_type=ErrorType.NETWORK,
                message="err", is_retryable=True, attempt=0,
            ))
        assert len(auditor.get_errors(source_id="a")) == 2
        assert len(auditor.get_errors(source_id="b")) == 1

    def test_auditor_clear(self):
        auditor = Auditor()
        auditor.record_error(ErrorRecord(
            timestamp=datetime.datetime.now(), source_id="t",
            state=None, error_type=ErrorType.NETWORK, message="err",
            is_retryable=True, attempt=0,
        ))
        assert len(auditor.get_errors()) == 1
        auditor.clear()
        assert len(auditor.get_errors()) == 0

    def test_auditor_last_error(self):
        auditor = Auditor()
        assert auditor.last_error() is None
        e1 = ErrorRecord(
            timestamp=datetime.datetime.now(), source_id="a",
            state=None, error_type=ErrorType.NETWORK, message="first",
            is_retryable=True, attempt=0,
        )
        e2 = ErrorRecord(
            timestamp=datetime.datetime.now(), source_id="b",
            state=None, error_type=ErrorType.NETWORK, message="second",
            is_retryable=True, attempt=0,
        )
        auditor.record_error(e1)
        auditor.record_error(e2)
        assert auditor.last_error().source_id == "b"


class TestCorruptedCache:
    def test_corrupted_cache_recovery(self):
        cache_path = "/tmp/test_meteomoris_cache.json"
        if os.path.exists(cache_path):
            os.remove(cache_path)
        with open(cache_path, "w") as f:
            f.write("{corrupted json")
        cache = Cache(cache_path=cache_path)
        assert cache.enabled
        result = cache.get("test_key")
        assert result is None
        assert os.path.exists(cache_path)
        os.remove(cache_path)

    def test_cache_get_stale(self):
        cache_path = "/tmp/test_meteomoris_stale.json"
        if os.path.exists(cache_path):
            os.remove(cache_path)
        cache = Cache(cache_path=cache_path)
        cache.set("key1", "fresh_value")
        with open(cache_path) as f:
            data = json.load(f)
        today = list(data.keys())[0]
        data["2024-01-01"] = {"key1": "stale_value"}
        with open(cache_path, "w") as f:
            json.dump(data, f)
        assert cache.get_stale("key1") == "stale_value"
        os.remove(cache_path)


class TestBackwardCompatibility:
    def test_result_unwraps_via_to_dict(self):
        from meteomoris.meteo import _to_dict
        r = Result(success=True, data={"forecast": "sunny"})
        result = _to_dict(r)
        assert result == {"forecast": "sunny"}

    def test_failed_result_unwraps_to_none(self):
        from meteomoris.meteo import _to_dict
        r = Result(success=False, data=None)
        result = _to_dict(r)
        assert result is None

    def test_failed_result_with_data_still_unwraps(self):
        from meteomoris.meteo import _to_dict
        r = Result(success=False, data={"partial": "data"})
        result = _to_dict(r)
        assert result == {"partial": "data"}

    def test_non_result_passes_through(self):
        from meteomoris.meteo import _to_dict
        assert _to_dict("hello") == "hello"
        assert _to_dict([1, 2, 3]) == [1, 2, 3]


class TestErrorRecord:
    def test_error_record_to_dict(self):
        ts = datetime.datetime(2026, 1, 15, 10, 30, 0)
        er = ErrorRecord(
            timestamp=ts, source_id="test", state=State.ERROR,
            error_type=ErrorType.PARSE, message="parse failed",
            is_retryable=False, attempt=2,
        )
        d = er.to_dict()
        assert d["source_id"] == "test"
        assert d["error_type"] == "PARSE"
        assert d["attempt"] == 2
        assert d["message"] == "parse failed"
        assert d["is_retryable"] is False


class TestFSMStates:
    def test_new_states_exist(self):
        assert State.RETRYING
        assert State.STALE_CACHE
        assert State.STALE_CACHE_CHECK
        assert State.DEGRADED
        assert State.ABORTED

    def test_new_events_exist(self):
        assert Event.TRANSIENT_FAILURE
        assert Event.PERMANENT_FAILURE
        assert Event.RETRY
        assert Event.RETRY_EXHAUSTED
        assert Event.STALE_FOUND
        assert Event.STALE_NOT_FOUND
        assert Event.CACHE_FAILED
        assert Event.ABORT
        assert Event.DEGRADE


class TestDispatchAudit:
    def test_dispatch_passes_auditor(self):
        dispatch = FSMDispatch()
        assert dispatch.auditor is not None

    def test_dispatch_returns_result(self):
        dispatch = FSMDispatch()
        dispatch.cache = FakeCache()
        dispatch.fetcher = FakeFetcher()
        dispatch.parser = FakeParser()
        result = dispatch.execute("weekforecast")
        assert isinstance(result, Result)
