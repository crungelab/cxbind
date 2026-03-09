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
        
    # For colorized terminal output (only active with -s or when pytest doesn't capture)
    stderr_id = logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        level="DEBUG",
        enqueue=False,
    )
    
    yield
    logger.remove(stderr_id)

@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    with caplog.at_level(logging.DEBUG):
        yield caplog
