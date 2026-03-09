from __future__ import annotations

import sys
import logging
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
BUILD_DIR = TESTS_DIR / "build"

if BUILD_DIR.exists():
    sys.path.insert(0, str(BUILD_DIR))

import pytest
from loguru import logger
from _pytest.logging import LogCaptureFixture

class PropagateHandler(logging.Handler):
    def emit(self, record):
        logging.getLogger(record.name).handle(record)

@pytest.fixture(autouse=True)
def newline_before_logs():
    sys.stdout.write("\n")
    sys.stdout.flush()
    yield

@pytest.fixture(autouse=True, scope="session")
def setup_loguru():
    logger.remove()
    
    # For pytest caplog/log-cli integration
    handler_id = logger.add(
        PropagateHandler(),
        format="{message}",
        level=0,
    )
    
    # For colorized terminal output (only active with -s or when pytest doesn't capture)
    stderr_id = logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        level="DEBUG",
        enqueue=False,
    )
    
    yield
    logger.remove(handler_id)
    logger.remove(stderr_id)
'''
@pytest.fixture(autouse=True, scope="session")
def setup_loguru():
    logger.remove()  # Remove default handler
    handler_id = logger.add(
        PropagateHandler(),
        format="{message}",
        level=0,  # Let stdlib logging handle level filtering
    )
    yield
    logger.remove(handler_id)
'''

@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    with caplog.at_level(logging.DEBUG):
        yield caplog
'''
class PropagateHandler(logging.Handler):
    def emit(self, record):
        logger = logging.getLogger(record.name)
        if logger.isEnabledFor(record.levelno):
            logger.handle(record)


@pytest.fixture(autouse=True, scope="session")
def cleanup_loguru():
    # Remove all handlers to make sure we don't interfere with tests.
    logger.remove()


@pytest.fixture(autouse=True, scope="session")
def propagate_loguru(cleanup_loguru):
    handler_id = logger.add(PropagateHandler(), format="{message}")
    yield
    logger.remove(handler_id)
'''

'''
@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    handler_id = logger.add(
        caplog.handler,
        format="\n{level:<7} {name}:{line} | {message}",
        level=0,
        filter=lambda record: record["level"].no >= caplog.handler.level,
        enqueue=False,  # Set to 'True' if your test is spawning child processes.
    )
    yield caplog
    logger.remove(handler_id)
'''

'''
@pytest.fixture(autouse=True)
def loguru_caplog(caplog: LogCaptureFixture):
    """
    Bridge Loguru logs into pytest's capture system.
    """

    handler_id = logger.add(
        caplog.handler,
        format="{level: <8} {message}",
        level="INFO",
    )

    yield caplog

    logger.remove(handler_id)
'''