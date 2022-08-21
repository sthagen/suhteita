import suhteita.suhteita as run


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


def test_two_sentences():
    wun, two = run.two_sentences(word_count=1)
    assert wun
    assert two
    assert ' ' not in wun
    assert ' ' not in two


def test_two_sentences_default():
    wun, two = run.two_sentences()
    assert wun
    assert two
    assert len(wun.split(' ')) == 4
    assert len(two.split(' ')) == 4


def test_extract_fields():
    fields = ('a', 'b')
    expectation = {field: 'x' for field in fields}
    assert expectation == run.extract_fields(expectation, fields)


def test_parse_request():
    assert run.parse_request([])


def test_parse_request_project():
    options = run.parse_request(['-p', 'project'])
    assert options
    assert options.target_project == 'project'


def test_parse_request_mode():
    options = run.parse_request(['--is-cloud'])
    assert options
    assert options.is_cloud


def test_login():
    run.Jira = Arij
    clk, service = run.login(target_url='target_url', user='user')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] < clk[2]
    assert service['fake'] == 'yes'


def test_get_server_info():
    run.Jira = Arij
    _, service = run.login(target_url='target_url', user='user')
    clk, info = run.get_server_info(service)
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] < clk[2]
    assert info['everything'] == 'fine'


def test_get_all_projects():
    run.Jira = Arij
    _, service = run.login(target_url='target_url', user='user')
    clk, projects = run.get_all_projects(service)
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] < clk[2]
    assert len(projects) == 2
    assert projects[0]['key'] == 'this'
    assert projects[1]['key'] == 'that'


def test_create_issue():
    run.Jira = Arij
    _, service = run.login(target_url='target_url', user='user')
    clk, x_key = run.create_issue(service, project='FOO', ts='so-what', description='nothing')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] < clk[2]
    assert x_key == 'FOO-42'


def test_issue_exists():
    run.Jira = Arij
    _, service = run.login(target_url='target_url', user='user')
    clk, exists = run.issue_exists(service, issue_key='')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert exists is False
    clk, exists = run.issue_exists(service, issue_key='FORREAL-42')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert exists is True


def test_create_issue_pair():
    run.Jira = Arij
    _, service = run.login(target_url='target_url', user='user')
    kwargs = dict(project='FOO', node='so-what', ts='time-flies', ident=('a b c d', 'e f g h'))
    clk, a_key, b_key = run.create_issue_pair(service, **kwargs)
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] < clk[2]
    assert a_key == 'FOO-42'
    assert b_key == 'FOO-42'
    kwargs = dict(project='', node='so-what', ts='time-flies', ident=('a b c d', 'e f g h'))
    clk, a_key, b_key = run.create_issue_pair(service, **kwargs)
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] < clk[2]
    assert a_key == ''
    assert b_key == ''


def test_load_issue():
    run.Jira = Arij
    _, service = run.login(target_url='target_url', user='user')
    clk, issue = run.load_issue(service, 'QUUX-1')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert issue['key'] == 'QUUX-1'


def test_execute_jql():
    run.Jira = Arij
    _, service = run.login(target_url='target_url', user='user')
    clk, results = run.execute_jql(service, 'key = FOO-42')
    assert len(clk) == 3
    assert int(clk[1]) >= 0
    assert clk[0] <= clk[2]
    assert results['issues'][0]['key'] == 'FOO-42'
