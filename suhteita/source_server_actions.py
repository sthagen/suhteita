"""Actions on source server instances."""
import copy
import datetime as dti
from typing import Dict, List, Tuple

from atlassian import Bitbucket  # type: ignore

from suhteita import IS_CLOUD, TOKEN, TS_FORMAT_PAYLOADS, Clocking


def login(target_url: str, user: str, password: str = TOKEN, is_cloud: bool = IS_CLOUD) -> Tuple[Clocking, Bitbucket]:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    service = Bitbucket(url=target_url, username=user, password=password, cloud=is_cloud)
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, service


def get_server_info(service: Bitbucket) -> Tuple[Clocking, object]:
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


def get_all_projects(service: Bitbucket) -> Tuple[Clocking, List[Dict[str, str]]]:
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
