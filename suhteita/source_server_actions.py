"""Actions on source server instances."""

import copy
import datetime as dti

from atlassian import Bitbucket

from suhteita import IS_CLOUD, TOKEN, TS_FORMAT_PAYLOADS, Clocking


def login(target_url: str, user: str, password: str = TOKEN, is_cloud: bool = IS_CLOUD) -> tuple[Clocking, Bitbucket]:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    service = Bitbucket(url=target_url, username=user, password=password, cloud=is_cloud)  # type: ignore
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, service


def get_server_info(service: Bitbucket) -> tuple[Clocking, object]:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    data = copy.deepcopy(service.get_server_info(True))  # type: ignore
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, data


def get_all_projects(service: Bitbucket) -> tuple[Clocking, list[dict[str, str]]]:
    """DRY."""
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    projects = copy.deepcopy(service.get_all_projects(included_archived=None))  # type: ignore
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    clocking: Clocking = (
        start_time.strftime(TS_FORMAT_PAYLOADS),
        (end_time - start_time).microseconds,
        end_time.strftime(TS_FORMAT_PAYLOADS),
    )
    return clocking, projects
