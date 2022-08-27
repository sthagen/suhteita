import suhteita.cli as cli
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


def test_setup_twenty_seven():
    options = cli.parse_request([])
    cfg = run.setup_twenty_seven(options)
    assert cfg.duplicate_labels == ['du', 'pli', 'ca', 'te']
