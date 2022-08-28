import datetime as dti
import logging
import os
import pathlib
import platform
import secrets
import uuid
from typing import Tuple, no_type_check

# [[[fill git_describe()]]]
__version__ = '2022.8.28+parent.09889aef'
# [[[end]]] (checksum: da5ccbf710f2439a095cf4a0ac6a98ec)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)

APP_ALIAS = 'suhteita'
APP_ENV = APP_ALIAS.upper()
DEBUG = os.getenv(f'{APP_ENV}_DEBUG', '')
ENCODING = 'utf-8'

NODE_INDICATOR = str(uuid.uuid3(uuid.NAMESPACE_DNS, platform.node()))
STORE = os.getenv(f'{APP_ENV}_STORE', '')  # default 'store' per argparse

USER = os.getenv(f'{APP_ENV}_USER', '')
TOKEN = os.getenv(f'{APP_ENV}_TOKEN', '')
BASE_URL = os.getenv(f'{APP_ENV}_BASE_URL', '')
IS_CLOUD = bool(os.getenv(f'{APP_ENV}_IS_CLOUD', ''))
PROJECT = os.getenv(f'{APP_ENV}_PROJECT', '')
IDENTITY = os.getenv(f'{APP_ENV}_IDENTITY', '')  # default 'adhoc' per argparse
WORDS = os.getenv(f'{APP_ENV}_WORDS', '/usr/share/dict/words')


log = logging.getLogger()  # Module level logger is sufficient
LOG_FOLDER = pathlib.Path('logs')
LOG_FILE = f'{APP_ALIAS}.log'
LOG_PATH = pathlib.Path(LOG_FOLDER, LOG_FILE) if LOG_FOLDER.is_dir() else pathlib.Path(LOG_FILE)
LOG_LEVEL = logging.INFO

TS_FORMAT_LOG = '%Y-%m-%dT%H:%M:%S'
TS_FORMAT_PAYLOADS = '%Y-%m-%d %H:%M:%S.%f UTC'

Clocking = Tuple[str, float, str]


def two_sentences(word_count: int = 4) -> Tuple[str, str]:
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
