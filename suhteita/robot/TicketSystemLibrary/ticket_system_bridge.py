"""Ticket system abstraction relaying keywords to API methods of the underlying ticket system (JRIA)."""
import ast
from typing import List, no_type_check

import wrapt  # type: ignore
from robot.api import ContinuableFailure, logger  # type: ignore

from suhteita.actions import Jira as Ticket


@no_type_check
def _string_to_data(string):
    """Parse the string into the underlying data type if successful else return the string."""
    try:
        return ast.literal_eval(str(string).strip())
    except Exception:
        return string


@no_type_check
@wrapt.decorator
def _string_variables_to_data(function, instance, args, kwargs):
    """Transform the string variables to data, relay to function, and return the call result."""
    args = [_string_to_data(arg) for arg in args]
    kwargs = dict((arg_name, _string_to_data(arg)) for arg_name, arg in kwargs.items())
    return function(*args, **kwargs)


@no_type_check
class TicketSystemBridge(object):
    """Use the robot framework hybrid API to proxy the calls and support discovery of keywords."""

    ROBOT_LIBRARY_SCOPE = 'Global'
    _ticket_system = Ticket
    _session = None

    def get_keyword_names(self) -> List[str]:
        """Generate the list of keywords from the underlying provider - required hybrid API method."""
        get_members = self._ticket_system.__dict__.items
        kws = [name for name, function in get_members() if hasattr(function, '__call__')]
        kws += ['extract_fields', 'ticket_session']

        return [kw for kw in kws if not kw.startswith('delete_') and kw not in ('__init__', 'get_issue_remotelinks')]

    @no_type_check
    def ticket_session(self, url=None, username=None, password=None, **kwargs):
        """Login and fetch the session object."""
        self._session = self._ticket_system(url=url, username=username, password=password, **kwargs)
        logger.debug('Connected to ticket system')
        return self._session

    @no_type_check
    @staticmethod
    def extract_fields(data, fields):
        """Extract dictionary fields from data to reduce the clutter in logs."""
        try:
            return {field: data[field] for field in fields}
        except KeyError as err:
            raise ContinuableFailure(f'Extraction of fields failed for (field=={err})')

    @no_type_check
    def __getattr__(self, name):
        """Relay the function matching the keyword or the lookup error."""
        func = None
        if name in self._ticket_system.__dict__.keys():
            func = getattr(self._ticket_system, name)

        if func:
            return _string_variables_to_data(func)

        raise AttributeError(f'Keyword {name} does not exist or has been overridden by this library.')
