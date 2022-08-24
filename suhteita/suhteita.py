#! /usr/bin/env python
"""Load the JIRA instance."""
import argparse
import copy
import datetime as dti
import json
import logging
import os
import pathlib
import platform
import secrets
import sys
import uuid
from typing import Dict, List, Tuple, Union, no_type_check

from atlassian import Jira  # type: ignore

APP_ALIAS = 'suhteita'
APP_ENV = APP_ALIAS.upper()
DEBUG = os.getenv(f'{APP_ENV}_DEBUG', '')
ENCODING = 'utf-8'

USER = os.getenv(f'{APP_ENV}_USER', '')
TOKEN = os.getenv(f'{APP_ENV}_TOKEN', '')
BASE_URL = os.getenv(f'{APP_ENV}_BASE_URL', '')
IS_CLOUD = bool(os.getenv(f'{APP_ENV}_IS_CLOUD', ''))
PROJECT = os.getenv(f'{APP_ENV}_PROJECT', '')
STORE = os.getenv(f'{APP_ENV}_STORE', '')  # default 'store' per argparse
IDENTITY = os.getenv(f'{APP_ENV}_IDENTITY', '')  # default 'adhoc' per argparse
WORDS = os.getenv(f'{APP_ENV}_WORDS', '/usr/share/dict/words')
NODE_INDICATOR = uuid.uuid3(uuid.NAMESPACE_DNS, platform.node())

log = logging.getLogger()  # Module level logger is sufficient
LOG_FOLDER = pathlib.Path('logs')
LOG_FILE = f'{APP_ALIAS}.log'
LOG_PATH = pathlib.Path(LOG_FOLDER, LOG_FILE) if LOG_FOLDER.is_dir() else pathlib.Path(LOG_FILE)
LOG_LEVEL = logging.INFO

TS_FORMAT_LOG = '%Y-%m-%dT%H:%M:%S'
TS_FORMAT_PAYLOADS = '%Y-%m-%d %H:%M:%S.%f UTC'
TS_FORMAT_STORE = '%Y%m%dT%H%M%S.%fZ'
Clocking = Tuple[str, float, str]


@no_type_check
class Store:
    @no_type_check
    def __init__(self, context: Dict[str, Union[str, dti.datetime]], folder_path: Union[pathlib.Path, str] = STORE):
        self.store = pathlib.Path(folder_path)
        self.identity = context['identity']
        self.start_time = context['start_time']
        self.end_ts = None
        self.total_secs = 0.0
        self.node_indicator = NODE_INDICATOR
        self.store.mkdir(parents=True, exist_ok=True)
        self.db_name = f'{self.identity}-{self.start_time.strftime(TS_FORMAT_STORE)}-{self.node_indicator}.json'
        self.rank = 0
        self.db = {
            '_meta': {
                'scenario': context.get('scenario', 'unknown'),
                'identity': self.identity,
                'node_indicator': str(self.node_indicator),
                'target': context.get('target', 'unknown'),
                'mode': context.get('mode', 'unknown'),
                'project': context.get('project', 'unknown'),
                'db_name': self.db_name,
                'db_path': str(self.store / self.db_name),
                'start_ts': self.start_time.strftime(TS_FORMAT_PAYLOADS),
                'total_secs': self.total_secs,
                'end_ts': self.end_ts,
                'has_failures_declared': None,
                'has_failures_detected': None,
            },
            'events': [],
        }

    @no_type_check
    def add(self, label: str, ok: bool, clk: Clocking, comment: str = ''):
        self.rank += 1
        self.db['events'].append(
            {
                'rank': self.rank,
                'label': label,
                'ok': ok,
                'start_ts': clk[0],
                'duration_usecs': clk[1],
                'end_ts': clk[2],
                'comment': comment,
            }
        )

    @no_type_check
    def dump(self, end_time: dti.datetime, has_failures: bool = False):
        self.end_time = end_time
        self.db['_meta']['end_ts'] = self.end_time.strftime(TS_FORMAT_PAYLOADS)
        self.db['_meta']['total_secs'] = (self.end_time - self.start_time).total_seconds()
        self.db['_meta']['has_failures_declared'] = has_failures
        detect_failures = False
        for event in self.db['events']:
            if not event['ok']:
                detect_failures = True
        self.db['_meta']['has_failures_detected'] = detect_failures
        with open(self.store / self.db_name, 'wt', encoding=ENCODING) as handle:
            json.dump(self.db, handle)


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


def two_sentences(word_count: int = 4) -> Tuple[str, str]:
    """DRY."""
    with open(WORDS, 'rt', encoding=ENCODING) as handle:
        words = [word.strip() for word in handle]
        wun = ' '.join(secrets.choice(words) for _ in range(word_count))
        two = ' '.join(secrets.choice(words) for _ in range(word_count))
        del words
    return wun, two


def login(target_url: str, user: str, password: str = TOKEN, is_cloud: bool = IS_CLOUD) -> Tuple[Clocking, Jira]:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    service = Jira(url=target_url, username=user, password=password, cloud=is_cloud)
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, service


def get_server_info(service: Jira) -> Tuple[Clocking, object]:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    data = copy.deepcopy(service.get_server_info(True))
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, data


def get_all_projects(service: Jira) -> Tuple[Clocking, List[Dict[str, str]]]:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    projects = copy.deepcopy(service.get_all_projects(included_archived=None))
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, projects


@no_type_check
def create_issue(service: Jira, project: str, ts: str, description: str) -> Tuple[Clocking, str]:
    """DRY."""
    fields = {
        'project': {'key': project},
        'issuetype': {'name': 'Task'},
        'summary': f'From REST we create at {ts}',
        'description': description,
    }
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    created = copy.deepcopy(service.issue_create(fields=fields))
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, created['key']


@no_type_check
def issue_exists(service: Jira, issue_key: str) -> Tuple[Clocking, bool]:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    exists = copy.deepcopy(service.issue_exists(issue_key))
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, exists


@no_type_check
def get_issue_status(service: Jira, issue_key: str) -> Tuple[Clocking, str]:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    status = copy.deepcopy(service.get_issue_status(issue_key))
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, status


def set_issue_status(service: Jira, issue_key: str, status: str) -> Tuple[Clocking, object]:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    response = copy.deepcopy(service.set_issue_status(issue_key, status))
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, response


def load_issue(service: Jira, issue_key: str) -> Tuple[Clocking, object]:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    data = copy.deepcopy(service.issue(issue_key))
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, data


@no_type_check
def execute_jql(service: Jira, query: str) -> Tuple[Clocking, object]:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    data = copy.deepcopy(service.jql(query))
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, data


@no_type_check
def amend_issue_description(service: Jira, issue_key: str, amendment: str, issue_context) -> Clocking:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    _ = copy.deepcopy(
        service.update_issue_field(
            issue_key,
            fields={'description': f"{issue_context['issues'][0]['fields']['description']}\n{amendment}"},
        )
    )
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking


@no_type_check
def add_comment(service: Jira, issue_key: str, comment: str) -> Tuple[Clocking, object]:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    response = copy.deepcopy(service.issue_add_comment(issue_key, comment))
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, response


@no_type_check
def extract_fields(data, fields):
    """DRY."""
    return {field: data[field] for field in fields}


def update_issue_field(service: Jira, issue_key: str, labels: List[str]) -> Clocking:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    _ = copy.deepcopy(service.update_issue_field(issue_key, fields={'labels': labels}))
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking


def create_duplicates_issue_link(
    service: Jira, duplicate_issue_key: str, original_issue_key: str
) -> Tuple[Clocking, object]:
    """DRY."""
    data = {
        'type': {'name': 'Duplicate'},
        'inwardIssue': {'key': duplicate_issue_key},
        'outwardIssue': {'key': original_issue_key},
        'comment': {
            'body': f'{duplicate_issue_key} truly duplicates {original_issue_key}!',
        },
    }
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    response = copy.deepcopy(service.create_issue_link(data))
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, response


def set_original_estimate(service: Jira, issue_key: str, hours: int) -> Tuple[Clocking, bool]:
    """DRY."""
    ok = True
    try:
        start_time = dti.datetime.now(tz=dti.timezone.utc)
        _ = copy.deepcopy(
            service.update_issue_field(issue_key, fields={'timetracking': {'originalEstimate': f'{hours}h'}})
        )
        end_time = dti.datetime.now(tz=dti.timezone.utc)
    except Exception as err:  # noqa
        end_time = dti.datetime.now(tz=dti.timezone.utc)
        ok = False
        log.error(f'Failed setting "{issue_key}".timetracking.originalEstimate to {hours} with (next error log line):')
        log.error(f'cont. ({err})')
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, ok


def create_component(service: Jira, project: str, name: str, description: str) -> Tuple[Clocking, str, str, object]:
    """DRY."""
    comp_data = {
        'project': project,
        'description': description,
        'name': name,
        'assigneeType': 'UNASSIGNED',
    }
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    comp_create_resp = copy.deepcopy(service.create_component(comp_data))
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    comp_id = comp_create_resp['id']
    return clocking, comp_id, name, service.component(comp_id)


def relate_issue_to_component(service: Jira, issue_key: str, comp_id: str, comp_name: str) -> Tuple[Clocking, bool]:
    """DRY."""
    ok = True
    try:
        start_time = dti.datetime.now(tz=dti.timezone.utc)
        _ = copy.deepcopy(service.update_issue_field(issue_key, fields={'components': [{'name': comp_name}]}))
        end_time = dti.datetime.now(tz=dti.timezone.utc)
    except Exception as err:  # noqa
        ok = False
        end_time = dti.datetime.now(tz=dti.timezone.utc)
        log.error(f'Not able to set component for issue: ({err}) Cleaning up - deleting component ID={comp_id}')
        service.delete_component(comp_id)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, ok


def parse_request(argv: List[str]) -> argparse.Namespace:
    """DRY."""
    parser = argparse.ArgumentParser(description=APP_ALIAS)
    parser.add_argument(
        '--user',
        '-u',
        dest='user',
        default=USER,
        help=f'user (default: {USER if USER else f"None, set {APP_ENV}_USER for default"})',
    )
    parser.add_argument(
        '--target',
        '-t',
        dest='target_url',
        default=BASE_URL,
        help=f'target URL (default: {BASE_URL if BASE_URL else f"None, set {APP_ENV}_BASE_URL for default"})',
    )
    parser.add_argument(
        '--is-cloud',
        action='store_true',
        dest='is_cloud',
        default=IS_CLOUD,
        help=(
            'target is cloud instance (default: '
            f'{"True" if IS_CLOUD else f"False, set {APP_ENV}_IS_CLOUD for a different default"})'
        ),
    )
    parser.add_argument(
        '--project',
        '-p',
        dest='target_project',
        default=PROJECT,
        help=f'target project (default: {PROJECT if PROJECT else f"None, set {APP_ENV}_PROJECT for default"})',
    )
    parser.add_argument(
        '--scenario',
        '-s',
        dest='scenario',
        default='unknown',
        help='scenario for recording (default: unknown)',
    )
    parser.add_argument(
        '--identity',
        '-i',
        dest='identity',
        default=IDENTITY if IDENTITY else 'adhoc',
        help=(
            'identity of take for recording'
            f' (default: {IDENTITY if IDENTITY else f"adhoc, set {APP_ENV}_IDENTITY for default"})'
        ),
    )
    parser.add_argument(
        '--out-path',
        '-o',
        dest='out_path',
        default=STORE if STORE else 'store',
        help=(
            'output folder path for recording'
            f' (default: {STORE if STORE else f"store, set {APP_ENV}_STORE for default"})'
        ),
    )
    return parser.parse_args(argv)


def main(argv: Union[List[str], None] = None, version: str = 'UNKNOWN') -> int:
    """Drive the transactions."""
    argv = sys.argv[1:] if argv is None else argv

    options = parse_request(argv)
    # Belt and braces:
    user = options.user if options.user else USER
    target_url = options.target_url if options.target_url else BASE_URL
    is_cloud = options.is_cloud if options.is_cloud else IS_CLOUD
    target_project = options.target_project if options.target_project else PROJECT
    scenario = options.scenario if options.scenario else 'unknown'
    identity = options.identity if options.identity else IDENTITY
    storage_path = options.out_path if options.out_path else STORE

    has_failures = False

    init_logger(name=APP_ENV, level=logging.DEBUG if DEBUG else None)
    if not TOKEN:
        log.error(f'No secret token or pass phrase given, please set {APP_ENV}_TOKEN accordingly')
        return 2

    log.info('=' * 84)
    log.info(f'Generator {APP_ALIAS} version {version}')
    log.info('# Prelude of a 27-steps scenario test execution')

    c_rand, d_rand = two_sentences()
    log.info(f'- Setup <01> Random sentence of original ({c_rand})')
    log.info(f'- Setup <02> Random sentence of duplicate ({d_rand})')

    random_component = secrets.token_urlsafe()
    log.info(f'- Setup <03> Random component name ({random_component})')

    todo, in_progress, done = ('to do', 'in progress', 'done')
    log.info(f'- Setup <04> The test workflow assumes the (case insensitive) states ({todo}, {in_progress}, {done})')

    ts = dti.datetime.now(tz=dti.timezone.utc).strftime(TS_FORMAT_PAYLOADS)
    log.info(f'- Setup <05> Timestamp marker in summaries will be ({ts})')

    desc_core = '... and short description we dictate.'
    log.info(f'- Setup <06> Common description part - of twin issues / pair - will be ({desc_core})')

    amendment = 'No, no, no. They duplicated me, help!'
    log.info(f'- Setup <07> Amendment for original description will be ({amendment})')

    fake_comment = 'I am the original, surely!'
    log.info(f'- Setup <08> Fake comment for duplicate will be ({fake_comment})')

    duplicate_labels = ['du', 'pli', 'ca', 'te']
    log.info(f'- Setup <09> Labels for duplicate will be ({duplicate_labels})')

    original_labels = ['for', 'real', 'highlander']
    log.info(f'- Setup <10> Labels for original will be ({original_labels})')

    hours_value = 42
    log.info(f'- Setup <11> Hours value for original estimate will be ({hours_value})')

    purge_me = 'SUHTEITA_PURGE_ME_ORIGINAL'
    log.info(f'- Setup <12> Purge indicator comment will be ({purge_me})')

    node_indicator = NODE_INDICATOR
    log.info(f'- Setup <13> Node indicator ({node_indicator})')
    log.info(
        f'- Setup <14> Connect will be to upstream ({"cloud" if is_cloud else "on-site"}) service ({target_url})'
        f' per login ({user})'
    )
    log.info('-' * 84)

    # Here we start the timer for the session:
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    start_ts = start_time.strftime(TS_FORMAT_PAYLOADS)
    context = {
        'target': target_url,
        'mode': f'{"cloud" if is_cloud else "on-site"}',
        'project': target_project,
        'scenario': scenario,
        'identity': identity,
        'start_time': start_time,
    }
    store = Store(context=context, folder_path=storage_path)
    log.info(f'# Starting 27-steps scenario test execution at at ({start_ts})')
    log.info('- Step <01> LOGIN')
    clk, service = login(target_url, user, password=TOKEN, is_cloud=is_cloud)
    log.info(f'^ Connected to upstream service; CLK={clk}')
    store.add('LOGIN', True, clk)

    log.info('- Step <02> SERVER_INFO')
    clk, server_info = get_server_info(service)
    log.info(f'^ Retrieved upstream server info cf. [SRV]; CLK={clk}')
    store.add('SERVER_INFO', True, clk, str(server_info))

    log.info('- Step <03> PROJECTS')
    clk, projects = get_all_projects(service)
    log.info(f'^ Retrieved {len(projects)} unarchived projects; CLK={clk}')
    store.add('PROJECTS', True, clk, f'count({len(projects)})')

    proj_env_ok = False
    if target_project:
        proj_env_ok = any((target_project == project['key'] for project in projects))

    if not proj_env_ok:
        log.error('Belt and braces - verify project selection:')
        log.info(json.dumps(sorted([project['key'] for project in projects]), indent=2))
        return 1

    first_proj_key = target_project if proj_env_ok else projects[0]['key']
    log.info(
        f'Verified target project from request ({target_project}) to be'
        f' {"" if proj_env_ok else "not "}present and set target project to ({first_proj_key})'
    )

    log.info('- Step <04> CREATE_ISSUE')
    clk, c_key = create_issue(
        service, first_proj_key, ts, description=f'{c_rand}\n{desc_core}\nCAUSALITY={node_indicator}'
    )
    log.info(f'^ Created original ({c_key}); CLK={clk}')
    store.add('CREATE_ISSUE', True, clk, 'original')

    log.info('- Step <05> ISSUE_EXISTS')
    clk, c_e = issue_exists(service, c_key)
    log.info(f'^ Existence of original ({c_key}) verified with result ({c_e}); CLK={clk}')
    store.add('ISSUE_EXISTS', bool(c_e), clk, 'original')

    log.info('- Step <06> CREATE_ISSUE')
    clk, d_key = create_issue(
        service, first_proj_key, ts, description=f'{d_rand}\n{desc_core}\nCAUSALITY={node_indicator}'
    )
    log.info(f'^ Created duplicate ({d_key}); CLK={clk}')
    store.add('CREATE_ISSUE', True, clk, 'duplicate')

    log.info('- Step <07> ISSUE_EXISTS')
    clk, d_e = issue_exists(service, d_key)
    log.info(f'^ Existence of duplicate ({d_key}) verified with result ({d_e}); CLK={clk}')
    store.add('ISSUE_EXISTS', bool(d_e), clk, 'duplicate')

    query = f'issue = {c_key}'
    log.info('- Step <08> EXECUTE_JQL')
    clk, c_q = execute_jql(service=service, query=query)
    log.info(f'^ Executed JQL({query}); CLK={clk}')
    store.add('EXECUTE_JQL', True, clk, f'query({query.replace(c_key, "original-key")})')

    log.info('- Step <09> AMEND_ISSUE_DESCRIPTION')
    clk = amend_issue_description(service, c_key, amendment=amendment, issue_context=c_q)
    log.info(f'^ Amended description of original {d_key} with ({amendment}); CLK={clk}')
    store.add('AMEND_ISSUE_DESCRIPTION', True, clk, 'original')

    log.info('- Step <10> ADD_COMMENT')
    clk, _ = add_comment(service=service, issue_key=d_key, comment=fake_comment)
    log.info(f'^ Added comment ({fake_comment}) to duplicate {d_key}; CLK={clk}')
    store.add('ADD_COMMENT', True, clk, 'duplicate')

    log.info('- Step <11> UPDATE_ISSUE_FIELD')
    clk = update_issue_field(service, d_key, labels=duplicate_labels)
    log.info(f'^ Updated duplicate {d_key} issue field of labels to ({duplicate_labels}); CLK={clk}')
    store.add('UPDATE_ISSUE_FIELD', True, clk, 'duplicate')

    log.info('- Step <12> UPDATE_ISSUE_FIELD')
    clk = update_issue_field(service, c_key, labels=original_labels)
    log.info(f'^ Updated original {c_key} issue field of labels to ({original_labels}); CLK={clk}')
    store.add('UPDATE_ISSUE_FIELD', True, clk, 'original')

    log.info('- Step <13> CREATE_DUPLICATES_ISSUE_LINK')
    clk, _ = create_duplicates_issue_link(service, c_key, d_key)
    log.info(f'^ Created link on duplicate stating it duplicates the original; CLK={clk}')
    store.add('CREATE_DUPLICATES_ISSUE_LINK', True, clk, 'dublicate duplicates original')

    log.info('- Step <14> GET_ISSUE_STATUS')
    clk, d_iss_state = get_issue_status(service, d_key)
    d_is_todo = d_iss_state.lower() == todo
    log.info(
        f'^ Retrieved status of the duplicate {d_key} as ({d_iss_state})'
        f' with result (is_todo == {d_is_todo}); CLK={clk}'
    )
    store.add('GET_ISSUE_STATUS', d_is_todo, clk, f'duplicate({d_iss_state})')

    log.info('- Step <15> SET_ISSUE_STATUS')
    clk, _ = set_issue_status(service, d_key, in_progress)
    log.info(f'^ Transitioned the duplicate {d_key} to ({in_progress}); CLK={clk}')
    store.add('SET_ISSUE_STATUS', True, clk, f'duplicate ({todo})->({in_progress})')

    log.info('- Step <16> SET_ISSUE_STATUS')
    clk, _ = set_issue_status(service, d_key, done)
    log.info(f'^ Transitioned the duplicate {d_key} to ({done}); CLK={clk}')
    store.add('SET_ISSUE_STATUS', True, clk, f'duplicate ({in_progress})->({done})')

    log.info('- Step <17> GET_ISSUE_STATUS')
    clk, d_iss_state_done = get_issue_status(service, d_key)
    d_is_done = d_iss_state_done.lower() == done
    log.info(
        f'^ Retrieved status of the duplicate {d_key} as ({d_iss_state_done})'
        f' with result (d_is_done == {d_is_done}); CLK={clk}'
    )
    store.add('GET_ISSUE_STATUS', d_is_done, clk, f'duplicate({d_iss_state_done})')

    log.info('- Step <18> ADD_COMMENT')
    clk, response_step_18_add_comment = add_comment(service, d_key, 'Closed as duplicate.')
    log.info(f'^ Added comment on {d_key} with response extract cf. [RESP-STEP-18]; CLK={clk}')
    store.add('ADD_COMMENT', True, clk, f'duplicate({response_step_18_add_comment["body"]})')

    log.info('- Step <19> SET_ORIGINAL_ESTIMATE')
    clk, ok = set_original_estimate(service, c_key, hours=hours_value)
    log.info(f'^ Added ({hours_value}) hours as original estimate to original {c_key} with result ({ok}); CLK={clk}')
    store.add('SET_ORIGINAL_ESTIMATE', ok, clk, 'original')

    log.info('- Step <20> GET_ISSUE_STATUS')
    clk, c_iss_state = get_issue_status(service, c_key)
    c_is_todo = c_iss_state.lower() == todo
    log.info(
        f'^ Retrieved status of the original {c_key} as ({c_iss_state})'
        f' with result (c_is_todo == {c_is_todo}); CLK={clk}'
    )
    store.add('GET_ISSUE_STATUS', c_is_todo, clk, f'original({c_iss_state})')

    log.info('- Step <21> SET_ISSUE_STATUS')
    clk, _ = set_issue_status(service, c_key, in_progress)
    log.info(f'^ Transitioned the original {c_key} to ({in_progress}); CLK={clk}')
    store.add('SET_ISSUE_STATUS', True, clk, f'original ({todo})->({in_progress})')

    log.info('- Step <22> GET_ISSUE_STATUS')
    clk, c_iss_state_in_progress = get_issue_status(service, c_key)
    c_is_in_progress = c_iss_state_in_progress.lower() == in_progress
    log.info(
        f'^ Retrieved status of the original {c_key} as ({c_iss_state_in_progress})'
        f' with result (c_is_in_progress == {c_is_in_progress}); CLK={clk}'
    )
    store.add('GET_ISSUE_STATUS', c_is_in_progress, clk, f'original({c_iss_state_in_progress})')

    log.info('- Step <23> CREATE_COMPONENT')
    clk, comp_id, a_component, comp_resp = create_component(
        service=service, project=first_proj_key, name=random_component, description=c_rand
    )
    log.info(f'^ Created component ({a_component}) with response extract cf. [RESP-STEP-23]; CLK={clk}')
    store.add('CREATE_COMPONENT', True, clk, f'component({comp_resp["description"]})')  # type: ignore

    log.info('- Step <24> RELATE_ISSUE_TO_COMPONENT')
    clk, ok = relate_issue_to_component(service, c_key, comp_id, a_component)
    log.info(
        f'^ Attempted relation of original {c_key} issue to component ({a_component}) with result ({ok}); CLK={clk}'
    )
    store.add('RELATE_ISSUE_TO_COMPONENT', ok, clk, 'original')
    if not ok:
        has_failures = True

    log.info('- Step <25> LOAD_ISSUE')
    clk, x_iss = load_issue(service, c_key)
    log.info(f'^ Loaded issue {c_key}; CLK={clk}')
    log.debug(json.dumps(x_iss, indent=2))
    store.add('LOAD_ISSUE', True, clk, 'original')

    log.info('- Step <26> ADD_COMMENT')
    clk, response_step_26_add_comment = add_comment(service=service, issue_key=c_key, comment=purge_me)
    log.info(f'^ Added purge tag comment on original {c_key} with response extract cf. [RESP-STEP-26]; CLK={clk}')
    store.add('ADD_COMMENT', True, clk, f'original({response_step_26_add_comment["body"]})')

    log.info('- Step <27> ADD_COMMENT')
    clk, response_step_27_add_comment = add_comment(service=service, issue_key=d_key, comment=purge_me)
    log.info(
        f'^ Added purge tag comment on duplicate issue {d_key} with response extract cf. [RESP-STEP-27]; CLK={clk}'
    )
    store.add('ADD_COMMENT', True, clk, f'duplicate({response_step_27_add_comment["body"]})')

    # Here we stop the timer for the session:
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    end_ts = end_time.strftime(TS_FORMAT_PAYLOADS)
    log.info(f'# Ended execution of 27-steps scenario test at ({end_ts})')
    log.info(f'Execution of 27-steps scenario test took {(end_time - start_time)} h:mm:ss.uuuuuu')
    log.info('-' * 84)

    log.info('# References:')
    log.info(f'[SRV]          Server info is ({server_info})')
    log.info(
        f'[RESP-STEP-18] Add comment response is'
        f' ({extract_fields(response_step_18_add_comment, fields=("self", "body"))})'
    )
    log.info(
        f'[RESP-STEP-23] Create component response is ({extract_fields(comp_resp, fields=("self", "description"))})'
    )
    log.info(
        f'[RESP-STEP-26] Add comment response is'
        f' ({extract_fields(response_step_26_add_comment, fields=("self", "body"))})'
    )
    log.info(
        f'[RESP-STEP-27] Add comment response is'
        f' ({extract_fields(response_step_27_add_comment, fields=("self", "body"))})'
    )
    log.info('-' * 84)

    log.info('Dumping records to store...')
    store.dump(end_time=end_time, has_failures=has_failures)
    log.info('-' * 84)

    log.info('OK')
    log.info('=' * 84)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))  # pragma: no cover
