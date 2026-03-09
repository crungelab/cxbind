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
    """Bridge loguru into stdlib logging for pytest caplog support."""
    def emit(self, record):
        logging.getLogger(record.name).handle(record)


@pytest.fixture(autouse=True, scope="session")
def setup_loguru(request):
    log_level = request.config.getoption("log_level", default="DEBUG")
    if log_level:
        log_level = log_level.upper()
    else:
        log_level = "DEBUG"
    logger.remove()

    # Colorized terminal output
    logger.add(
        sys.stdout,
        #format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        level=log_level,
        enqueue=False,
    )

    # Propagate into stdlib logging for caplog assertion support
    logger.add(PropagateHandler(), format="{message}", level=0)

    yield
    logger.remove()

@pytest.fixture(autouse=True)
def newline_before_logs():
    """Ensure logs start on a new line after pytest's test name output."""
    sys.stdout.write("\n")
    sys.stdout.flush()
    yield


@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    """Capture loguru output via PropagateHandler for log assertions."""
    with caplog.at_level(logging.DEBUG):
        yield caplog