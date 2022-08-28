import re

import pytest
from robot.api import ContinuableFailure

import suhteita.actions as actions
from suhteita.robot.TicketSystemLibrary import TicketSystemBridge, TicketSystemLibrary


class Arij(dict):
    def factory(self, url='target_url', username='user', password='password', cloud=False):
        self['fake'] = 'yes'

    def __init__(self, url='target_url', username='user', password='password', cloud=False):
        self.factory(url, username, password, cloud)

    def get_server_info(self, foo: bool):
        return {'everything': 'fine', 'foo': foo}

    def get_all_projects(self, included_archived=None):
        if included_archived is None:
            return [{'key': 'this'}, {'key': 'that'}]
        else:
            return [{'key': 'this'}, {'key': 'that'}, {'key': 'attic'}]


def test_tsb_class():
    tsb = TicketSystemBridge()
    assert tsb


def test_tsb_get_keyword_names():
    tsb = TicketSystemBridge()
    names = tsb.get_keyword_names()
    assert '__init__' not in names
    assert all(not name.startswith('delete_') for name in names)


def test_tsb_extract_fields():
    tsb = TicketSystemBridge()
    assert tsb.extract_fields({'a': 42, 'b': False}, fields=['a']) == {'a': 42}


def test_tsb_extract_fields_sad():
    tsb = TicketSystemBridge()
    message = r"Extraction of fields failed for (field=='a')"
    with pytest.raises(ContinuableFailure, match=re.escape(message)):
        tsb.extract_fields({'b': False}, fields=['a'])


def test_tsb_extract_paths():
    tsb = TicketSystemBridge()
    assert tsb.extract_paths({'a': {'aa': {'aaa': 42}}, 'b': False}, paths=['/a/aa/aaa']) == {'/a/aa/aaa': 42}


def test_tsb_extract_project_keys():
    tsb = TicketSystemBridge()
    assert tsb.extract_project_keys([{'key': 42}, {'yek': -1, 'key': 'PRJ'}]) == [42, 'PRJ']


def test_tsb_extract_project_keys_sad():
    tsb = TicketSystemBridge()
    message = r"Extraction of key field failed for projects (field=='key')"
    with pytest.raises(ContinuableFailure, match=re.escape(message)):
        tsb.extract_project_keys([{'key': -42}, {'yek': -2}])


def test_tsl_extract_project_keys():
    tsl = TicketSystemLibrary()
    assert tsl.extract_project_keys([{'key': 'SOMEPROJECT'}, {'yek': -3, 'key': 'X'}]) == ['SOMEPROJECT', 'X']


def test_tsl_keyword_sad():
    tsl = TicketSystemLibrary()

    class Thing:
        pass

    thing = Thing()
    message = r'Keyword delete_everything does not exist or has been overridden by this library.'
    with pytest.raises(AttributeError, match=re.escape(message)):
        tsl.delete_everything(thing, 'does-not-exist-42', delete_subtasks=False)


def test_tsl_keyword():
    actions.Jira = Arij
    tsl = TicketSystemLibrary()
    session = tsl.ticket_session()
    assert session
