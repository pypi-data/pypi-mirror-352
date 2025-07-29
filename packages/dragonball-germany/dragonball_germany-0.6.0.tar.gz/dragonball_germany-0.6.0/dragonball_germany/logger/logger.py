import logging
import logging.config
import os

DEFAULT_FORMAT: str = '%(asctime)s [%(levelname)s] %(message)s'
DEFAULT_DATEFMT: str = '%Y-%m-%d %H:%M:%S'
DEFAULT_LOG_LEVEL: str = 'info'
LOG_LEVELS: dict[str, int] = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'notset': logging.NOTSET,
}


def get_logger(name: str = __name__) -> logging.Logger:
    return logging.getLogger(name=name)


def setup_logging() -> None:
    log_level_env: str = os.getenv('LOG_LEVEL', DEFAULT_LOG_LEVEL).lower()
    level = LOG_LEVELS.get(log_level_env, LOG_LEVELS[DEFAULT_LOG_LEVEL])

    logging.config.dictConfig(
        {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'custom': {
                    'format': DEFAULT_FORMAT,
                    'datefmt': DEFAULT_DATEFMT,
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'custom',
                },
            },
            'root': {
                'handlers': ['console'],
                'level': level,
            },
            'loggers': {
                'uvicorn': {
                    'handlers': ['console'],
                    'level': level,
                    'propagate': False,
                },
                'uvicorn.error': {
                    'handlers': ['console'],
                    'level': level,
                    'propagate': False,
                },
                'uvicorn.access': {
                    'handlers': ['console'],
                    'level': level,
                    'propagate': False,
                },
            },
        }
    )
