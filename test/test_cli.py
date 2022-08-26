import logging

import pytest  # type: ignore

import suhteita.cli as cli
import suhteita.suhteita as impl


def test_main_nok_too_many_arguments():
    message = r'main\(\) takes from 0 to 1 positional arguments but 2 were given'
    with pytest.raises(TypeError, match=message):
        cli.main(1, 2)


def test_main_ok_smvp(capsys):
    with pytest.raises(SystemExit, match='0'):
        cli.main(['-h'])
    out, err = capsys.readouterr()
    assert not err
    assert 'show this help message and exit' in out
    assert 'output folder path for recording' in out


def test_main(caplog):
    impl.TOKEN = ''
    assert 2 == cli.main(['-p', 'XYZ'])
    message = 'No secret token or pass phrase given, please set SUHTEITA_TOKEN accordingly'
    assert caplog.record_tuples == [('SUHTEITA', logging.ERROR, message)]


def test_parse_request():
    assert cli.parse_request([])


def test_parse_request_project():
    options = cli.parse_request(['-p', 'project'])
    assert options
    assert options.target_project == 'project'


def test_parse_request_mode():
    options = cli.parse_request(['--is-cloud'])
    assert options
    assert options.is_cloud
