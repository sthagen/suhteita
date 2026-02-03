"""Relationships (Finnish: suhteita) maintained across distances as load test core."""

import datetime as dti
import logging
import os
import pathlib
import platform
import secrets
import uuid
from typing import no_type_check

# [[[fill git_describe()]]]
__version__ = '2026.2.3+parent.g88869d4b'
# [[[end]]] (checksum: ba0cb34713c384ef259040e3a0d1bb03)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)

APP_ALIAS = str(pathlib.Path(__file__).parent.name)
APP_ENV = APP_ALIAS.upper()
APP_NAME = locals()['__doc__']
DEBUG = bool(os.getenv(f'{APP_ENV}_DEBUG', ''))
VERBOSE = bool(os.getenv(f'{APP_ENV}_VERBOSE', ''))
QUIET = False
STRICT = bool(os.getenv(f'{APP_ENV}_STRICT', ''))
ENCODING = 'utf-8'
ENCODING_ERRORS_POLICY = 'ignore'
DEFAULT_CONFIG_NAME = f'.{APP_ALIAS}.json'

NODE_INDICATOR = str(uuid.uuid3(uuid.NAMESPACE_DNS, platform.node()))
STORE = os.getenv(f'{APP_ENV}_STORE', '')  # default 'store' per argparse
COMMA = ','
VERSION = __version__
VERSION_INFO = __version_info__

USER = os.getenv(f'{APP_ENV}_USER', '')
TOKEN = os.getenv(f'{APP_ENV}_TOKEN', '')
BASE_URL = os.getenv(f'{APP_ENV}_BASE_URL', '')
IS_CLOUD = bool(os.getenv(f'{APP_ENV}_IS_CLOUD', ''))
PROJECT = os.getenv(f'{APP_ENV}_PROJECT', '')
IDENTITY = os.getenv(f'{APP_ENV}_IDENTITY', '')  # default 'adhoc' per argparse
WORDS = os.getenv(f'{APP_ENV}_WORDS', '/usr/share/dict/words')
WORKFLOW_CSV = os.getenv(f'{APP_ENV}_WORKFLOW_CSV', 'to do,in progress,done')

log = logging.getLogger()  # Module level logger is sufficient
LOG_FOLDER = pathlib.Path('logs')
LOG_FILE = f'{APP_ALIAS}.log'
LOG_PATH = pathlib.Path(LOG_FOLDER, LOG_FILE) if LOG_FOLDER.is_dir() else pathlib.Path(LOG_FILE)
LOG_LEVEL = logging.INFO

TS_FORMAT_LOG = '%Y-%m-%dT%H:%M:%S'
TS_FORMAT_PAYLOADS = '%Y-%m-%d %H:%M:%S.%f UTC'

Clocking = tuple[str, float, str]

__all__ = [
    'APP_ALIAS',
    'APP_ENV',
    'APP_NAME',
    'COMMA',
    'DEBUG',
    'DEFAULT_CONFIG_NAME',
    'ENCODING',
    'ENCODING_ERRORS_POLICY',
    'IDENTITY',
    'LOG_FILE',
    'LOG_LEVEL',
    'LOG_PATH',
    'NODE_INDICATOR',
    'PROJECT',
    'QUIET',
    'STORE',
    'STRICT',
    'TS_FORMAT_LOG',
    'TS_FORMAT_PAYLOADS',
    'VERBOSE',
    'VERSION',
    'VERSION_INFO',
    'WORDS',
    'WORKFLOW_CSV',
    'Clocking',
]


def two_sentences(word_count: int = 4) -> tuple[str, str]:
    """DRY."""
    with open(WORDS, 'rt', encoding=ENCODING) as handle:
        words = [word.strip() for word in handle]
        wun = ' '.join(secrets.choice(words) for _ in range(word_count))
        two = ' '.join(secrets.choice(words) for _ in range(word_count))
        del words
    return wun, two


@no_type_check
def extract_fields(data, fields):
    """DRY."""
    return {field: data[field] for field in fields}


@no_type_check
def formatTime_RFC3339(self, record, datefmt=None):
    """HACK A DID ACK we could inject .astimezone() to localize ..."""
    return dti.datetime.fromtimestamp(record.created, dti.timezone.utc).isoformat()


@no_type_check
def init_logger(name=None, level=None):
    """Initialize module level logger"""
    global log  # pylint: disable=global-statement

    log_format = {
        'format': '%(asctime)s %(levelname)s [%(name)s]: %(message)s',
        'datefmt': TS_FORMAT_LOG,
        # 'filename': LOG_PATH,
        'level': LOG_LEVEL if level is None else level,
    }
    logging.Formatter.formatTime = formatTime_RFC3339
    logging.basicConfig(**log_format)
    log = logging.getLogger(APP_ENV if name is None else name)
    log.propagate = True


init_logger(name=APP_ENV, level=logging.DEBUG if DEBUG else None)
