from loguru import logger

from .session import Session

class WorkContext:
    def __init__(self) -> None:
        pass

    @property
    def current_session(self) -> Session:
        return Session.get_current()