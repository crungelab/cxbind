from typing import TYPE_CHECKING, Optional, Type, Dict, List, Any, Callable
import contextlib
from contextvars import ContextVar

from loguru import logger

from .session import Session
from .node import Node

current_pod: ContextVar[Optional["Pod"]] = ContextVar("current_pod", default=None)

class Pod:
    def __init__(self, node: Node) -> None:
        self.node = node

    @property
    def current_session(self) -> Session:
        return Session.get_current()
    
    def make_current(self):
        current_pod.set(self)

    @classmethod
    def get_current(cls) -> Optional["Pod"]:
        return current_pod.get()
