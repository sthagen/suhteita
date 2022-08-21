import suhteita.suhteita as run


class Arij(dict):
    def factory(self, url='target_url', username='user', password='password', cloud=False):
        self['fake'] = 'yes'

    def __init__(self, url='target_url', username='user', password='password', cloud=False):
        self.factory(url='target_url', username='user', password='password', cloud=False)

    def get_server_info(self, foo: bool):
        return {'everything': 'fine', 'foo': foo}

    def get_all_projects(self, included_archived=None):
        if included_archived is None:
            return [{'key': 'this'}, {'key': 'that'}]
        else:
            return [{'key': 'this'}, {'key': 'that'}, {'key': 'attic'}]


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
