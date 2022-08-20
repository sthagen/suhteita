#! /usr/bin/env python
"""Load the JIRA instance."""
import argparse
import datetime as dti
import json
import logging
import os
import pathlib
import platform
import secrets
import sys
import uuid
from typing import List, Tuple, Union, no_type_check

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

log = logging.getLogger()  # Module level logger is sufficient
LOG_FOLDER = pathlib.Path('logs')
LOG_FILE = f'{APP_ALIAS}.log'
LOG_PATH = pathlib.Path(LOG_FOLDER, LOG_FILE) if LOG_FOLDER.is_dir() else pathlib.Path(LOG_FILE)
LOG_LEVEL = logging.INFO


@no_type_check
def init_logger(name=None, level=None):
    """Initialize module level logger"""
    global log  # pylint: disable=global-statement

    log_format = {
        'format': '%(asctime)s.%(msecs)03d %(levelname)s [%(name)s]: %(message)s',
        'datefmt': '%Y-%m-%dT%H:%M:%S',
        # 'filename': LOG_PATH,
        'level': LOG_LEVEL if level is None else level,
    }
    logging.basicConfig(**log_format)
    log = logging.getLogger(APP_ENV if name is None else name)
    log.propagate = True


def two_sentences(word_count: int = 4) -> Tuple[str, str]:
    """DRY."""
    with open('/usr/share/dict/words', 'rt', encoding=ENCODING) as handle:
        words = [word.strip() for word in handle]
        wun = ' '.join(secrets.choice(words) for _ in range(word_count))
        two = ' '.join(secrets.choice(words) for _ in range(word_count))
        del words
    return wun, two


def create_issue_pair(service: Jira, project: str, node: uuid.UUID, ts: str, ident: Tuple[str, str]) -> Tuple[str, str]:
    """DRY."""
    desc_core = '... and short description we dictate.'
    log.info(f'Common description part will be ({desc_core})')
    c_desc = f'{ident[0]}\n{desc_core}\nCAUSALITY={node}'
    d_desc = f'{ident[1]}\n{desc_core}\nCAUSALITY={node}'
    fields = {
        'project': {'key': project},
        'issuetype': {'name': 'Task'},
        'summary': f'From REST we create at {ts}',
        'description': c_desc,
    }
    created = service.issue_create(fields=fields)
    c_key = created['key']
    if not service.issue_exists(c_key):
        log.error(f'Failed existence test for original ({c_key})')
    fields['description'] = d_desc
    duplicate = service.issue_create(fields=fields)
    d_key = duplicate['key']
    if not service.issue_exists(d_key):
        log.error(f'Failed existence test for original ({d_key})')
    return c_key, d_key


@no_type_check
def execute_jql(service: Jira, query: str):
    """DRY."""
    return service.jql(query)


@no_type_check
def amend_issue_description(service: Jira, issue_key: str, amendment: str, issue_context) -> None:
    """DRY."""
    service.update_issue_field(
        issue_key,
        fields={'description': f"{issue_context['issues'][0]['fields']['description']}\n{amendment}"},
    )


@no_type_check
def add_comment(service: Jira, issue_key: str, comment: str):
    """DRY."""
    return service.issue_add_comment(issue_key, comment)


def update_issue_field(service: Jira, issue_key: str, labels: List[str]) -> None:
    """DRY."""
    service.update_issue_field(issue_key, fields={'labels': labels})


def create_duplicates_issue_link(service: Jira, duplicate_issue_key: str, original_issue_key: str) -> None:
    """DRY."""
    data = {
        'type': {'name': 'Duplicate'},
        'inwardIssue': {'key': duplicate_issue_key},
        'outwardIssue': {'key': original_issue_key},
        'comment': {
            'body': f'{duplicate_issue_key} truly duplicates {original_issue_key}!',
        },
    }
    service.create_issue_link(data)


def create_component(service: Jira, project: str, description: str) -> Tuple[str, str, object]:
    """DRY."""
    random_component = secrets.token_urlsafe()
    log.info(f'Random component will be ({random_component})')
    comp_data = {
        'project': project,
        'description': description,
        'name': random_component,
        'assigneeType': 'UNASSIGNED',
    }
    log.info(f'Creating random component ({random_component})')
    comp_create_resp = service.create_component(comp_data)
    comp_id = comp_create_resp['id']
    return comp_id, random_component, service.component(comp_id)


def parse_request(argv: List[str]) -> argparse.Namespace:
    """DRY."""
    parser = argparse.ArgumentParser(description=APP_ALIAS)
    parser.add_argument(
        '--user',
        '-u',
        dest='user',
        default=USER,
        help=f'user (default: {USER if USER else "None, set {APP_ENV}_USER for default"})',
    )
    parser.add_argument(
        '--target',
        '-t',
        dest='target_url',
        default=BASE_URL,
        help=f'target URL (default: {BASE_URL if BASE_URL else "None, set {APP_ENV}_BASE_URL for default"})',
    )
    parser.add_argument(
        '--project',
        '-p',
        dest='target_project',
        default=PROJECT,
        help=f'target project (default: {PROJECT if PROJECT else "None, set {APP_ENV}_PROJECT for default"})',
    )
    parser.add_argument(
        '--is-cloud',
        action='store_true',
        dest='is_cloud',
        default=IS_CLOUD,
        help=(
            'target is cloud instance (default: '
            f'{"True" if IS_CLOUD else "False, set {APP_ENV}_IS_CLOUD for a different default"})'
        ),
    )
    return parser.parse_args(argv)


def main(argv: Union[List[str], None] = None) -> int:
    """Drive the transactions."""
    argv = sys.argv[1:] if argv is None else argv

    options = parse_request(argv)
    # Belt and braces:
    user = options.user if options.user else USER
    target_url = options.target_url if options.target_url else BASE_URL
    target_project = options.target_project if options.target_project else PROJECT
    is_cloud = options.is_cloud if options.is_cloud else IS_CLOUD

    init_logger(name=APP_ENV, level=logging.DEBUG if DEBUG else None)
    if not TOKEN:
        log.error(f'No secret token or pass phrase given, please set {APP_ENV}_TOKEN accordingly')
        return 2

    node_indicator = uuid.uuid3(uuid.NAMESPACE_DNS, platform.node())
    c_rand, d_rand = two_sentences()

    start_time = dti.datetime.now(tz=dti.timezone.utc)
    start_ts = start_time.strftime('%Y-%m-%d %H:%M:%S.%f UTC')
    log.info(f'Starting load test execution at at ({start_ts})')
    log.info(f'Node indicator ({node_indicator})')
    log.info(
        f'Connecting to upstream ({"cloud" if is_cloud else "on-site"}) service ({target_url})'
        f' per login ({user}) at ({start_ts})'
    )
    service = Jira(url=target_url, username=user, password=TOKEN, cloud=is_cloud)
    log.info('Connected to upstream service ... retrieve server info')
    log.info(json.dumps(service.get_server_info(True), indent=2))

    log.info(f'Random sentence of original ({c_rand})')
    log.info(f'Random sentence of duplicate ({d_rand})')
    projects = service.get_all_projects(included_archived=None)
    proj_env_ok = False
    if target_project:
        proj_env_ok = any((target_project == project['key'] for project in projects))
        log.info(f'Verified target project from reques ({target_project}) to be {"" if proj_env_ok else "not "}present')

    if not proj_env_ok:
        log.error('Belt and braces - verify project selection:')
        log.info(json.dumps(sorted([project['key'] for project in projects]), indent=2))
        return 1

    first_proj_key = target_project if proj_env_ok else projects[0]['key']
    log.info(f'Target project set to ({first_proj_key})')

    ts = dti.datetime.now(tz=dti.timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f UTC')
    log.info(f'Timestamp marker in summaries will be ({ts})')

    c_key, d_key = create_issue_pair(service, first_proj_key, node_indicator, ts, ident=(c_rand, d_rand))
    log.info(f'Generated two issues: original ({c_key}) and duplicate ({d_key})')

    c_q = execute_jql(service=service, query=f'issue = {c_key}')

    amend_issue_description(service, c_key, amendment='No, no, no. They duplicated me, help!', issue_context=c_q)

    _ = add_comment(service=service, issue_key=d_key, comment='I am the original, surely!')

    update_issue_field(service, d_key, labels=['du', 'pli', 'ca', 'te'])
    update_issue_field(service, c_key, labels=['for', 'real', 'highlander'])

    create_duplicates_issue_link(service, c_key, d_key)

    todo, in_progress, done = ('To Do', 'In Progress', 'Done')
    log.info(f'The test workflow assumes the states ({todo}, {in_progress}, {done})')

    d_iss_state = service.get_issue_status(d_key)
    if d_iss_state != todo:
        log.error(f'Unexpected state ({d_iss_state}) for duplicate {d_key} - expected was ({todo})')

    log.info(f'Transitioning the duplicate {d_key} to ({in_progress})')
    service.set_issue_status(d_key, in_progress)

    log.info(f'Transitioning the duplicate {d_key} to ({done})')
    service.set_issue_status(d_key, done)
    d_iss_state_done = service.get_issue_status(d_key)
    if d_iss_state_done != done:
        log.error(f'Unexpected state ({d_iss_state}) for duplicate {d_key} - expected was ({done})')

    d_comment_resp_closing = add_comment(service, d_key, 'Closed as duplicate.')
    log.info(f'Adding comment on {d_key} had response ({str(d_comment_resp_closing)})')

    hours = 42
    log.info(f'Non-zero original time estimate will be ({hours}h)')
    try:
        _ = service.update_issue_field(c_key, fields={'timetracking': {'originalEstimate': f'{hours}h'}})
        log.info(f'Set "{c_key}".timetracking.originalEstimate to {hours}')
    except Exception as err:  # noqa
        log.error(f'Failed setting "{c_key}".timetracking.originalEstimate to {hours} with (next error log line):')
        log.error(f'cont. ({err})')
        log.warning('These can be license issues - verify timetracking works in the web ui')
        log.info('Ignoring the problem ...')

    c_iss_state = service.get_issue_status(c_key)
    if c_iss_state != todo:
        log.error(f'Unexpected state ({c_iss_state}) for original {c_key} - expected was ({todo})')

    log.info(f'Transitioning the original {c_key} to ({in_progress})')
    service.set_issue_status(c_key, in_progress)
    c_iss_state_in_progress = service.get_issue_status(c_key)
    if c_iss_state_in_progress != in_progress:
        log.error(f'Unexpected state ({c_iss_state_in_progress}) for original {c_key} - expected was ({in_progress})')

    comp_id, a_component, comp_resp = create_component(service=service, project=first_proj_key, description=c_rand)
    log.info(f'Created component {a_component} with response ({str(comp_resp)})')

    try:
        log.info(f'Associating the original {c_key} with random component ({a_component})')
        service.update_issue_field(c_key, fields={'components': [{'name': a_component}]})
    except Exception as err:  # noqa
        service.delete_component(comp_id)
        log.error(f'Not able to set component for issue: {err}')

    log.info(f'Loading issue ({c_key}) wun more time')
    x_iss = service.issue(c_key)
    log.debug(json.dumps(x_iss, indent=2))

    log.info('Adding comments to the created issues tagging for deletion')
    c_comment_resp = add_comment(service=service, issue_key=c_key, comment='SUHTEITA_PURGE_ME_ORIGINAL')
    log.info(f'Added purge tag comment on original {c_key} with response ({str(c_comment_resp)})')

    d_comment_resp = add_comment(service=service, issue_key=d_key, comment='SUHTEITA_PURGE_ME_DUPLICATE')
    log.info(f'Added purge tag comment to the duplicate issue {d_key} with response ({str(d_comment_resp)})')

    end_time = dti.datetime.now(tz=dti.timezone.utc)
    end_ts = end_time.strftime('%Y-%m-%d %H:%M:%S.%f UTC')
    log.info(f'Ended execution of load test at ({end_ts})')
    log.info(f'Execution of load test took {(end_time - start_time)} h:mm:ss.uuuuuu')

    log.info('OK')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
