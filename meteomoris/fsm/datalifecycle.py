from .states import State, Event


class DataLifecycleFSM:
    TRANSITIONS = {
        (State.IDLE, Event.REQUEST): (State.CACHE_CHECK, "_on_cache_check"),
        (State.CACHE_CHECK, Event.CACHE_HIT): (State.CACHE_HIT, "_on_cache_hit"),
        (State.CACHE_CHECK, Event.CACHE_MISS): (State.CACHE_MISS, None),
        (State.CACHE_HIT, Event.DATA_READY): (State.DATA_READY, None),
        (State.CACHE_MISS, Event.INTERNET_OK): (State.FETCHING, "_on_fetch"),
        (State.CACHE_MISS, Event.NO_INTERNET): (State.NO_INTERNET, "_on_no_internet"),
        (State.FETCHING, Event.FETCHED): (State.PARSING, "_on_parse"),
        (State.FETCHING, Event.FETCH_FAILED): (State.ERROR, "_on_error"),
        (State.PARSING, Event.PARSED): (State.CACHING, "_on_cache_save"),
        (State.PARSING, Event.PARSE_FAILED): (State.ERROR, "_on_error"),
        (State.CACHING, Event.CACHED): (State.DATA_READY, None),
        (State.CACHING, Event.DATA_READY): (State.DATA_READY, None),
        (State.NO_INTERNET, Event.ERROR_HANDLED): (State.ERROR, "_on_error"),
        (State.DATA_READY, Event.RENDER): (State.RENDERING, "_on_render"),
        (State.DATA_READY, Event.RETURN): (State.RETURNING, "_on_return"),
        (State.RENDERING, Event.RENDERED): (State.RETURNING, "_on_return"),
        (State.RETURNING, Event.RETURN): (State.COMPLETED, None),
        (State.ERROR, Event.RETURN): (State.COMPLETED, "_on_error_return"),
    }

    def __init__(self, source_spec, cache, fetcher, parser, renderer):
        self.state = State.IDLE
        self.source = source_spec
        self.cache = cache
        self.fetcher = fetcher
        self.parser = parser
        self.renderer = renderer
        self.data = None
        self.html = None
        self.error = None

    def _get_next(self, event):
        return self.TRANSITIONS.get((self.state, event))

    def _transition(self, event):
        entry = self._get_next(event)
        if entry is None:
            raise RuntimeError(
                "Invalid transition: {} from {} with {}".format(
                    event, self.state, event
                )
            )
        next_state, action_name = entry
        self.state = next_state
        if action_name:
            handler = getattr(self, action_name, None)
            if handler:
                handler()

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
                        return None
                    self._transition(Event.INTERNET_OK)
                else:
                    self._transition(Event.INTERNET_OK)

            if self.state == State.FETCHING:
                self.html = self.fetcher.fetch(
                    self.source["url"],
                )
                if self.html is None:
                    self._transition(Event.FETCH_FAILED)
                    return None
                self._transition(Event.FETCHED)

            if self.state == State.PARSING:
                parser_method = getattr(
                    self.parser, self.source["parser"], None
                )
                if parser_method is None:
                    self._transition(Event.PARSE_FAILED)
                    return None
                result = parser_method(self.html, **params)
                if result is None:
                    self._transition(Event.PARSE_FAILED)
                    return None
                self.data = result
                self._transition(Event.PARSED)

            if self.state == State.CACHING:
                cache_key = self.source.get("cache_key")
                if cache_key and self.cache.enabled:
                    self.cache.set(cache_key, self._data_to_cache())
                self._transition(Event.CACHED)

            if self.state == State.DATA_READY and print_output:
                self._transition(Event.RENDER)

            if self.state == State.RENDERING:
                self._on_render(**params)
                self._transition(Event.RENDERED)

            if self.state in (State.RETURNING, State.COMPLETED):
                self._transition(Event.RETURN)
                return self.data

            self._transition(Event.RETURN)
            return self.data

        except Exception as e:
            self.error = e
            self.state = State.ERROR
            return None

    def _data_to_cache(self):
        if hasattr(self.data, "to_dict"):
            return self.data.to_dict()
        if isinstance(self.data, list):
            return [d.to_dict() if hasattr(d, "to_dict") else d for d in self.data]
        if isinstance(self.data, dict):
            return {
                k: v.to_dict() if hasattr(v, "to_dict") else v
                for k, v in self.data.items()
            }
        return self.data

    def _on_cache_check(self):
        pass

    def _on_cache_hit(self):
        pass

    def _on_fetch(self):
        pass

    def _on_parse(self):
        pass

    def _on_cache_save(self):
        pass

    def _on_no_internet(self):
        if self.source["requires_internet"]:
            print("No internet")
            import sys
            sys.exit()

    def _on_render(self, **params):
        render_method = getattr(self.renderer, "render_" + self.source["parser"].replace("parse_", ""), None)
        if render_method:
            render_method(self.data, **params)

    def _on_return(self):
        pass

    def _on_error(self):
        pass

    def _on_error_return(self):
        pass
