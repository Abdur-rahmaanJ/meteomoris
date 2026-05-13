from ..model.sources import DATASOURCES
from ..behavior.cache import Cache
from ..behavior.fetcher import Fetcher
from ..behavior.parser import Parser
from ..behavior.renderer import Renderer
from ..behavior.auditor import Auditor
from ..behavior.retry import RetryPolicy
from .datalifecycle import DataLifecycleFSM


class FSMDispatch:
    def __init__(self):
        self.cache = Cache()
        self.fetcher = Fetcher()
        self.parser = Parser()
        self.renderer = Renderer()
        self.auditor = Auditor()

    def execute(self, source_id, print_output=False, **params):
        source = DATASOURCES.get(source_id)
        if source is None:
            raise ValueError("Unknown data source: {}".format(source_id))
        fsm = DataLifecycleFSM(
            source, self.cache, self.fetcher, self.parser, self.renderer,
            auditor=self.auditor,
        )
        return fsm.execute(print_output=print_output, **params)
