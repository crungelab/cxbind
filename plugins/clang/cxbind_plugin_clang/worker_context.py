from loguru import logger

from cxbind.unit import Unit

from .session import Session

class WorkerContext:
    def __init__(self) -> None:
        pass

    @property
    def current_session(self) -> Session:
        return Session.get_current()