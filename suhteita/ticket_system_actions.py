"""Actions on JIRA instances."""
import copy
import datetime as dti
from typing import Dict, List, Tuple, no_type_check

from atlassian import Jira  # type: ignore

from suhteita import IS_CLOUD, TOKEN, TS_FORMAT_PAYLOADS, Clocking, log


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
