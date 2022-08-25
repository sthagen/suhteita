#! /usr/bin/env python
"""Login and request server info from a JIRA instance."""
import datetime as dti
import logging
import sys
from typing import List, Union

import suhteita.suhteita as api
from suhteita import __version__ as version


def main(argv: Union[List[str], None] = None) -> int:
    """Drive the ping."""
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
    api.log.info('# Prelude of a 27-steps scenario test execution')

    ts = dti.datetime.now(tz=dti.timezone.utc).strftime(api.TS_FORMAT_PAYLOADS)
    api.log.info(f'- Setup <01> Timestamp marker in summaries will be ({ts})')

    node_indicator = api.NODE_INDICATOR
    api.log.info(f'- Setup <ß2> Node indicator ({node_indicator})')
    api.log.info(
        f'- Setup <ß3> Connect will be to upstream ({"cloud" if is_cloud else "on-site"}) service ({target_url})'
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
    api.log.info(f'# Starting 2-steps ping test execution at at ({start_ts})')
    api.log.info('- Step <01> LOGIN')
    clk, service = api.login(target_url, user, password=api.TOKEN, is_cloud=is_cloud)
    api.log.info(f'^ Connected to upstream service; CLK={clk}')
    store.add('LOGIN', True, clk)

    api.log.info('- Step <02> SERVER_INFO')
    clk, server_info = api.get_server_info(service)
    api.log.info(f'^ Retrieved upstream server info cf. [SRV]; CLK={clk}')
    store.add('SERVER_INFO', True, clk, str(server_info))

    # Here we stop the timer for the session:
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    end_ts = end_time.strftime(api.TS_FORMAT_PAYLOADS)
    api.log.info(f'# Ended execution of 2-steps ping test at ({end_ts})')
    api.log.info(f'Execution of 2-steps ping test took {(end_time - start_time)} h:mm:ss.uuuuuu')
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
