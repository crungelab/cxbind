from loguru import logger

from cxbind import CxBind
from cxbind.plugin import Plugin

from .clang_runner_factory import ClangRunnerFactory


class ClangPlugin(Plugin):
    def __init__(self):
        super().__init__()

    def install(self, app: CxBind):
        app.register_runner_factory("clang", ClangRunnerFactory())
