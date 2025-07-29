import logging

import pytest
from pytest import MonkeyPatch

from dragonball_germany.logger import get_logger as get_logger
from dragonball_germany.logger import setup_logging as setup_logging


def test_get_logger_returns_logger_instance() -> None:
    logger: logging.Logger = get_logger('test_logger')
    assert isinstance(logger, logging.Logger)
    assert logger.name == 'test_logger'


@pytest.mark.parametrize(
    'env_value, expected_level',
    [
        ('critical', logging.CRITICAL),
        ('error', logging.ERROR),
        ('warning', logging.WARNING),
        ('info', logging.INFO),
        ('debug', logging.DEBUG),
        ('notset', logging.NOTSET),
        ('invalid_level', logging.INFO),  # fallback to default
        ('', logging.INFO),  # empty string fallback to default
    ],
)
def test_setup_logging_log_level_env(
    monkeypatch: MonkeyPatch, env_value: str, expected_level: int
) -> None:
    if env_value == '':
        monkeypatch.delenv('LOG_LEVEL', raising=False)
    else:
        monkeypatch.setenv('LOG_LEVEL', env_value)

    setup_logging()
    logger: logging.Logger = logging.getLogger()
    assert logger.level == expected_level


def test_setup_logging_sets_handlers() -> None:
    setup_logging()
    logger: logging.Logger = logging.getLogger()

    # Check that the root logger has at least one StreamHandler (console)
    handlers = logger.handlers
    assert any(isinstance(h, logging.StreamHandler) for h in handlers)

    # Check formatter of the first handler (console)
    formatter = handlers[0].formatter
    assert formatter is not None
    assert formatter._fmt == '%(asctime)s [%(levelname)s] %(message)s'
    assert formatter.datefmt == '%Y-%m-%d %H:%M:%S'
