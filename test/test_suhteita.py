import suhteita.suhteita as run


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
