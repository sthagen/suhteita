#! /usr/bin/env python
"""Login, request server info and projects from a JIRA instance, and create an issue."""
import datetime as dti
import logging
import sys
from typing import List, Union

import suhteita.suhteita as api
from suhteita import __version__ as version

APPLICATION_FOR_LOG = 'CREATOR'


def main(argv: Union[List[str], None] = None) -> int:
    """Drive the creation."""
    argv = sys.argv[1:] if argv is None else argv

    options = api.parse_request(argv)
    # Belt and braces:
    user = options.user if options.user else api.USER
    target_url = options.target_url if options.target_url else api.BASE_URL
    is_cloud = options.is_cloud if options.is_cloud else api.IS_CLOUD
    target_project = options.target_project if options.target_project else api.PROJECT
    scenario = options.scenario if options.scenario else 'unknown'
    identity = options.identity if options.identity else api.IDENTITY
    storage_path = options.out_path if options.out_path else api.STORE

    has_failures = False

    api.init_logger(name=api.APP_ENV, level=logging.DEBUG if api.DEBUG else None)
    if not api.TOKEN:
        api.log.error(f'No secret token or pass phrase given, please set {api.APP_ENV}_TOKEN accordingly')
        return 2

    api.log.info('=' * 84)
    api.log.info(f'Generator {api.APP_ALIAS} version {version}')
    api.log.info('# Prelude of a 4-steps creator test execution')

    c_rand, _ = api.two_sentences()
    api.log.info(f'- Setup <01> Random sentence of original ({c_rand})')

    ts = dti.datetime.now(tz=dti.timezone.utc).strftime(api.TS_FORMAT_PAYLOADS)
    api.log.info(f'- Setup <02> Timestamp marker in summaries will be ({ts})')

    desc_core = '... and short description we dictate.'
    api.log.info(f'- Setup <03> Common description part - of twin issues / pair - will be ({desc_core})')

    node_indicator = api.NODE_INDICATOR
    api.log.info(f'- Setup <04> Node indicator ({node_indicator})')
    api.log.info(
        f'- Setup <05> Connect will be to upstream ({"cloud" if is_cloud else "on-site"}) service ({target_url})'
        f' per login ({user})'
    )
    api.log.info('-' * 84)

    # Here we start the timer for the session:
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    start_ts = start_time.strftime(api.TS_FORMAT_PAYLOADS)
    context = {
        'target': target_url,
        'mode': f'{"cloud" if is_cloud else "on-site"}',
        'project': target_project,
        'scenario': scenario,
        'identity': identity,
        'start_time': start_time,
    }
    store = api.Store(context=context, folder_path=storage_path)
    api.log.info(f'# Starting 4-steps creator test execution at at ({start_ts})')
    api.log.info('- Step <01> LOGIN')
    clk, service = api.login(target_url, user, password=api.TOKEN, is_cloud=is_cloud)
    api.log.info(f'^ Connected to upstream service; CLK={clk}')
    store.add('LOGIN', True, clk)

    api.log.info('- Step <02> SERVER_INFO')
    clk, server_info = api.get_server_info(service)
    api.log.info(f'^ Retrieved upstream server info cf. [SRV]; CLK={clk}')
    store.add('SERVER_INFO', True, clk, str(server_info))

    api.log.info('- Step <03> PROJECTS')
    clk, projects = api.get_all_projects(service)
    api.log.info(f'^ Retrieved {len(projects)} unarchived projects; CLK={clk}')
    store.add('PROJECTS', True, clk, f'count({len(projects)})')

    proj_env_ok = False
    if target_project:
        proj_env_ok = any((target_project == project['key'] for project in projects))

    if not proj_env_ok:
        api.log.error('Belt and braces - verify project selection:')
        api.log.info(api.json.dumps(sorted([project['key'] for project in projects]), indent=2))
        return 1

    first_proj_key = target_project if proj_env_ok else projects[0]['key']
    api.log.info(
        f'Verified target project from request ({target_project}) to be'
        f' {"" if proj_env_ok else "not "}present and set target project to ({first_proj_key})'
    )

    api.log.info('- Step <04> CREATE_ISSUE')
    clk, c_key = api.create_issue(
        service, first_proj_key, ts, description=f'{c_rand}\n{desc_core}\nCAUSALITY={node_indicator}'
    )
    api.log.info(f'^ Created original ({c_key}); CLK={clk}')
    store.add('CREATE_ISSUE', True, clk, 'original')

    # Here we stop the timer for the session:
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    end_ts = end_time.strftime(api.TS_FORMAT_PAYLOADS)
    api.log.info(f'# Ended execution of 4-steps creator test at ({end_ts})')
    api.log.info(f'Execution of 4-steps creator test took {(end_time - start_time)} h:mm:ss.uuuuuu')
    api.log.info('-' * 84)

    api.log.info('# References:')
    api.log.info(f'[SRV]          Server info is ({server_info})')
    api.log.info('-' * 84)

    api.log.info('Dumping records to store...')
    store.dump(end_time=end_time, has_failures=has_failures)
    api.log.info('-' * 84)

    api.log.info('OK')
    api.log.info('=' * 84)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))  # pragma: no cover
