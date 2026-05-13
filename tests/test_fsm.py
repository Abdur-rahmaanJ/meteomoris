from meteomoris.fsm.states import State, Event
from meteomoris.fsm.datalifecycle import DataLifecycleFSM
from meteomoris.fsm.dispatch import FSMDispatch
from meteomoris.model.sources import DATASOURCES
from meteomoris.model.entities import Result


class FakeCache:
    def __init__(self):
        self.enabled = True
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def get_stale(self, key):
        return None

    def set(self, key, data):
        self._store[key] = data


class FakeFetcher:
    def __init__(self, online=True, html="<html></html>"):
        self.online = online
        self.html = html
        self.check_count = 0

    def check_internet(self):
        self.check_count += 1
        return self.online

    def fetch(self, url):
        class FakeResponse:
            def __init__(self, content):
                self.content = content
                self.text = content if isinstance(content, str) else content.decode()
        return FakeResponse(self.html)


class FakeParser:
    def parse_weekforecast(self, html):
        return ["fake_forecast"]

    def parse_moonphase(self, html):
        return {"moon": "phase"}


class FakeRenderer:
    def __init__(self):
        self.rendered = []

    def render_weekforecast(self, data, **kwargs):
        self.rendered.append(("weekforecast", data, kwargs))

    def render_moonphase(self, data, **kwargs):
        self.rendered.append(("moonphase", data, kwargs))


def make_fsm(source_id, cache=None, fetcher=None, parser=None, renderer=None):
    from meteomoris.behavior.auditor import Auditor
    from meteomoris.behavior.retry import RetryPolicy
    source = dict(DATASOURCES[source_id])
    return DataLifecycleFSM(
        source,
        cache or FakeCache(),
        fetcher or FakeFetcher(),
        parser or FakeParser(),
        renderer or FakeRenderer(),
        auditor=Auditor(),
        retry_policy=RetryPolicy(max_retries=0),
    )


class TestStateTransitions:
    def test_cache_hit_flow(self):
        cache = FakeCache()
        cache.set("weekforecast", ["cached_data"])
        renderer = FakeRenderer()
        fsm = make_fsm("weekforecast", cache=cache, renderer=renderer)

        result = fsm.execute(print_output=False)

        assert result.success
        assert result.data == ["cached_data"]
        assert fsm.state == State.COMPLETED

    def test_cache_hit_with_print(self):
        cache = FakeCache()
        cache.set("weekforecast", ["cached_data"])
        renderer = FakeRenderer()
        fsm = make_fsm("weekforecast", cache=cache, renderer=renderer)

        result = fsm.execute(print_output=True)

        assert result.success
        assert result.data == ["cached_data"]
        assert fsm.state == State.COMPLETED

    def test_cache_miss_fetch_and_parse(self):
        cache = FakeCache()
        renderer = FakeRenderer()
        fsm = make_fsm("weekforecast", cache=cache, renderer=renderer)

        result = fsm.execute(print_output=False)

        assert result.success
        assert result.data == ["fake_forecast"]
        assert fsm.state == State.COMPLETED

    def test_cache_miss_with_print(self):
        cache = FakeCache()
        renderer = FakeRenderer()
        fsm = make_fsm("weekforecast", cache=cache, renderer=renderer)

        result = fsm.execute(print_output=True)

        assert result.success
        assert result.data == ["fake_forecast"]
        assert len(renderer.rendered) == 1
        assert renderer.rendered[0][0] == "weekforecast"

    def test_no_internet_returns_error(self):
        cache = FakeCache()
        fetcher = FakeFetcher(online=False)
        fsm = make_fsm("weekforecast", cache=cache, fetcher=fetcher)

        result = fsm.execute(print_output=False)

        assert not result.success

    def test_cache_stores_data(self):
        cache = FakeCache()
        fsm = make_fsm("weekforecast", cache=cache)
        fsm.execute(print_output=False)

        assert cache.get("weekforecast") == ["fake_forecast"]

    def test_invalid_state_raises_error(self):
        fsm = make_fsm("weekforecast")
        try:
            fsm._transition(Event.RENDER)
            assert False, "Should have raised"
        except RuntimeError:
            pass

    def test_execute_with_moonphase(self):
        cache = FakeCache()
        renderer = FakeRenderer()
        fsm = make_fsm("moonphase", cache=cache, renderer=renderer)

        result = fsm.execute(print_output=True)

        assert result.success
        assert result.data == {"moon": "phase"}
        assert len(renderer.rendered) == 1
        assert renderer.rendered[0][0] == "moonphase"

    def test_second_call_uses_cache(self):
        cache = FakeCache()
        fsm = make_fsm("weekforecast", cache=cache)
        fsm.execute(print_output=False)

        fsm2 = make_fsm("weekforecast", cache=cache)
        result = fsm2.execute(print_output=False)

        assert result.success
        assert result.data == ["fake_forecast"]

    def test_fetch_failure_returns_error(self):
        class FailingFetcher(FakeFetcher):
            def fetch(self, url):
                return None

        cache = FakeCache()
        fsm = make_fsm("weekforecast", cache=cache, fetcher=FailingFetcher())
        result = fsm.execute(print_output=False)
        assert not result.success

    def test_result_has_error_metadata(self):
        class FailingFetcher(FakeFetcher):
            def fetch(self, url):
                return None

        cache = FakeCache()
        fsm = make_fsm("weekforecast", cache=cache, fetcher=FailingFetcher())
        result = fsm.execute(print_output=False)
        assert not result.success
        assert len(result.errors) > 0
        assert result.error is not None


class TestFSMDispatch:
    def test_dispatch_creates_fsm(self):
        dispatch = FSMDispatch()
        dispatch.cache = FakeCache()
        dispatch.fetcher = FakeFetcher()
        dispatch.parser = FakeParser()

        result = dispatch.execute("weekforecast")
        assert isinstance(result, Result)
        assert result.success
        assert result.data == ["fake_forecast"]

    def test_dispatch_unknown_source(self):
        dispatch = FSMDispatch()
        try:
            dispatch.execute("nonexistent")
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_all_sources_have_valid_config(self):
        for source_id, config in DATASOURCES.items():
            assert "url" in config or config.get("cache_key")
            assert "parser" in config
            assert "requires_internet" in config

    def test_all_transitions_defined(self):
        for (state, event), value in DataLifecycleFSM.TRANSITIONS.items():
            assert isinstance(state, State)
            assert isinstance(event, Event)
            assert isinstance(value, State)
