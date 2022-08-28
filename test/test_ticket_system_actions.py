import pytest

import suhteita.ticket_system_actions as actions
from suhteita import extract_fields


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

    def issue_create(self, fields):
        project = fields['project']['key']
        return {'key': f'{project}-42' if project else ''}

    def issue_exists(self, key: str):
        return bool(key)

    def issue(self, key: str):
        return {'key': key}

    def jql(self, query: str):
        return {'issues': [{'key': 'FOO-42'}]}

    def issue_add_comment(self, key: str, comment: str):
        return {'key': key, 'body': comment}

    def update_issue_field(self, issue_key: str, fields):
        if issue_key == 'raise':
            raise Exception('You asked for it!')
        return {'key': issue_key, 'fields': {**fields}}

    def create_issue_link(self, data):
        return {**data}

    def delete_component(self, that):
        return that

    def create_component(self, data):
        return {'id': '123', **data}

    def component(self, comp_id: str):
        return {'self': 'https://example.com/component/123', 'description': 'ABC', 'name': 'oops'}

    def get_issue_status(self, issue_key):
        return 'status-value'

    def set_issue_status(self, issue_key, status):
        return None


def test_login():
    actions.Jira = Arij
    clk, service = actions.login(target_url='target_url', user='user')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] < clk[2]
    assert service['fake'] == 'yes'


def test_get_server_info():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    clk, info = actions.get_server_info(service)
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] < clk[2]
    assert info['everything'] == 'fine'


def test_get_all_projects():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    clk, projects = actions.get_all_projects(service)
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] < clk[2]
    assert len(projects) == 2
    assert projects[0]['key'] == 'this'
    assert projects[1]['key'] == 'that'


def test_create_issue():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    clk, x_key = actions.create_issue(service, project='FOO', ts='so-what', description='nothing')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] < clk[2]
    assert x_key == 'FOO-42'


def test_issue_exists():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    clk, exists = actions.issue_exists(service, issue_key='')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert exists is False
    clk, exists = actions.issue_exists(service, issue_key='FORREAL-42')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert exists is True


def test_load_issue():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    clk, issue = actions.load_issue(service, 'QUUX-1')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert issue['key'] == 'QUUX-1'


def test_execute_jql():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    clk, results = actions.execute_jql(service, 'key = FOO-42')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert results['issues'][0]['key'] == 'FOO-42'


def test_add_comment():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    clk, response = actions.add_comment(service, issue_key='BAZ-42', comment='no-comment')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    some = extract_fields(response, fields=['key', 'body'])
    assert some == {'key': 'BAZ-42', 'body': 'no-comment'}


def test_update_issue_field():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    clk = actions.update_issue_field(service, issue_key='BAR-101', labels=['yes', 'but', 'no'])
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]


def test_create_duplicates_issue_link():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    clk, response = actions.create_duplicates_issue_link(
        service, duplicate_issue_key='BAR-42', original_issue_key='BAR-101'
    )
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    some = extract_fields(response, fields=('inwardIssue', 'outwardIssue'))
    assert some == {'inwardIssue': {'key': 'BAR-42'}, 'outwardIssue': {'key': 'BAR-101'}}


def test_set_original_estimate():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    clk, ok = actions.set_original_estimate(service, issue_key='BAR-42', hours=123)
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert ok
    clk, ok = actions.set_original_estimate(service, issue_key='raise', hours=-1)
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert not ok


def test_relate_issue_to_component():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    clk, ok = actions.relate_issue_to_component(service, issue_key='K', comp_id='123', comp_name='a-comp')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert ok
    clk, ok = actions.relate_issue_to_component(service, issue_key='raise', comp_id='1', comp_name='n/a')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert not ok


def test_create_component():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    clk, comp_id, random_component, response = actions.create_component(service, project='X', name='Y', description='Z')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert comp_id == '123'
    some = extract_fields(response, fields=('self', 'description', 'name'))
    assert some == {'self': 'https://example.com/component/123', 'description': 'ABC', 'name': 'oops'}
    assert random_component == 'Y'


def test_amend_issue_description():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    ctx = {'issues': [{'fields': {'description': 'D'}}]}
    clk = actions.amend_issue_description(service, issue_key='F1', amendment='A', issue_context=ctx)
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    with pytest.raises(Exception, match=r'You asked for it!'):
        actions.amend_issue_description(service, issue_key='raise', amendment='X', issue_context=ctx)


def test_get_issue_status():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    clk, status = actions.get_issue_status(service, issue_key='BAR-42')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert status == 'status-value'


def test_set_issue_status():
    actions.Jira = Arij
    _, service = actions.login(target_url='target_url', user='user')
    clk, response = actions.set_issue_status(service, issue_key='BAR-42', status='something-brittle')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert response is None
