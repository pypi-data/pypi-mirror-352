import logging.config
import pathlib
from typing import Mapping as _Mapping
from typing import Sequence as _Sequence

import yaml

logger = logging.getLogger(__name__)


class Configuration(dict):

    def __init__(self, *args, **kwargs):
        super().__init__()
        super().__setattr__("__dict__", self)
        for k, v in dict(*args, **kwargs).items():
            super().__setattr__(k, self.__wrap(v))

    def __setattr__(self, key, value):
        super().__setattr__(key, self.__wrap(value))

    def __setitem__(self, key, value):
        super().__setattr__(key, self.__wrap(value))

    @classmethod
    def __wrap(cls, obj):
        if isinstance(obj, _Mapping):
            return cls(obj)
        if isinstance(obj, _Sequence) and \
                not isinstance(obj, str):
            return [cls.__wrap(o) for o in obj]
        return obj


def load_config(config: pathlib.Path | dict | str) -> Configuration:
    if isinstance(config, str):
        try:
            config = yaml.safe_load(open(config).read())
        except:
            logger.debug(f"failed to load configuration file from string '{config}'", exc_info=True)
    elif isinstance(config, dict):
        config = config
    elif isinstance(config, pathlib.Path):
        config = yaml.safe_load(config.read_text("r", encoding="utf8"))

    return Configuration(config)


def configure_logging():
    config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {'colored': {'()': 'fastapis.common.loggers.CustomFormatter',
                                   'datefmt': '%(asctime)s'},
                       'json': {'()': 'fastapis.common.loggers.CustomJSONFormatter',
                                'datefmt': '%(asctime)s'}},
        'handlers': {'console': {'level': 20,
                                 'formatter': 'colored',
                                 'class': 'logging.StreamHandler',
                                 'stream': 'ext://sys.stdout'},
                     'file': {'level': 10,
                              'formatter': 'json',
                              'class': 'logging.handlers.RotatingFileHandler',
                              'filename': 'app.log',
                              'maxBytes': 1048576,
                              'backupCount': 3}},
        'loggers': {'root': {'handlers': ['console'],
                             'level': 'INFO',
                             'propagate': False},
                    'uvicorn': {'handlers': ['console', 'file'],
                                'level': 'DEBUG',
                                'propagate': False},
                    'uvicorn.access': {'handlers': ['console', 'file'],
                                       'level': 'DEBUG',
                                       'propagate': False},
                    'uvicorn.error': {'handlers': ['console', 'file'],
                                      'level': 'DEBUG',
                                      'propagate': False},
                    'uvicorn.asgi': {'handlers': ['console'],
                                     'level': 'DEBUG',
                                     'propagate': False}}}
    logging.config.dictConfig(config)
