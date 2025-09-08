from loguru import logger

from .session import Session

class WorkerContext:
    def __init__(self, session: Session) -> None:
        self.session = session
