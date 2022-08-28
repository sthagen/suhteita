#! /usr/bin/env python
"""Login and request server info from a JIRA instance."""
import argparse
import datetime as dti
import logging
import sys
from typing import List, Union, no_type_check

import suhteita
import suhteita.cli as cli
import suhteita.ticket_system_actions as actions
from suhteita import (
    BASE_URL,
    IDENTITY,
    IS_CLOUD,
    NODE_INDICATOR,
    PROJECT,
    STORE,
    TOKEN,
    TS_FORMAT_PAYLOADS,
    USER,
    __version__ as version,
    log,
)
from suhteita.store import Store

APPLICATION_FOR_LOG = 'PING'


@no_type_check
def setup_scenario(options: argparse.Namespace) -> object:
    """Setup the scenario adn return the parameters as members of an object."""

    class Setup:
        pass

    setup = Setup()

    setup.user = options.user if options.user else USER
    setup.target_url = options.target_url if options.target_url else BASE_URL
    setup.is_cloud = options.is_cloud if options.is_cloud else IS_CLOUD
    setup.target_project = options.target_project if options.target_project else PROJECT
    setup.scenario = options.scenario if options.scenario else 'unknown'
    setup.identity = options.identity if options.identity else IDENTITY
    setup.storage_path = options.out_path if options.out_path else STORE

    log.info('=' * 84)
    log.info(f'Generator {suhteita.APP_ALIAS} version {version}')
    log.info('# Prelude of a 2-steps ping test execution')

    setup.ts = dti.datetime.now(tz=dti.timezone.utc).strftime(TS_FORMAT_PAYLOADS)
    log.info(f'- Setup <01> Timestamp marker in summaries will be ({setup.ts})')

    setup.node_indicator = NODE_INDICATOR
    log.info(f'- Setup <02> Node indicator ({setup.node_indicator})')
    log.info(
        f'- Setup <03> Connect will be to upstream ({"cloud" if setup.is_cloud else "on-site"})'
        f' service ({setup.target_url}) per login ({setup.user})'
    )
    log.info('-' * 84)

    return setup


def main(argv: Union[List[str], None] = None) -> int:
    """Drive the ping."""
    argv = sys.argv[1:] if argv is None else argv
    options = cli.parse_request(argv)

    suhteita.init_logger(name=APPLICATION_FOR_LOG, level=logging.DEBUG if suhteita.DEBUG else None)
    if not TOKEN:
        suhteita.log.error(f'No secret token or pass phrase given, please set {suhteita.APP_ENV}_TOKEN accordingly')
        return 2

    cfg = setup_scenario(options=options)

    # Belt and braces:
    has_failures = False

    # Here we start the timer for the session:
    start_time = dti.datetime.now(tz=dti.timezone.utc)
    start_ts = start_time.strftime(suhteita.TS_FORMAT_PAYLOADS)
    context = {
        'target': cfg.target_url,
        'mode': f'{"cloud" if cfg.is_cloud else "on-site"}',
        'project': cfg.target_project,
        'scenario': cfg.scenario,
        'identity': cfg.identity,
        'start_time': start_time,
    }
    store = Store(context=context, setup=cfg, folder_path=cfg.storage_path)
    log.info(f'# Starting 2-steps ping test execution at at ({start_ts})')
    log.info('- Step <01> LOGIN')
    clk, service = actions.login(cfg.target_url, cfg.user, password=suhteita.TOKEN, is_cloud=cfg.is_cloud)
    log.info(f'^ Connected to upstream service; CLK={clk}')
    store.add('LOGIN', True, clk)

    log.info('- Step <02> SERVER_INFO')
    clk, server_info = actions.get_server_info(service)
    log.info(f'^ Retrieved upstream server info cf. [SRV]; CLK={clk}')
    store.add('SERVER_INFO', True, clk, str(server_info))

    # Here we stop the timer for the session:
    end_time = dti.datetime.now(tz=dti.timezone.utc)
    end_ts = end_time.strftime(TS_FORMAT_PAYLOADS)
    log.info(f'# Ended execution of 2-steps ping test at ({end_ts})')
    log.info(f'Execution of 2-steps ping test took {(end_time - start_time)} h:mm:ss.uuuuuu')
    log.info('-' * 84)

    log.info('# References:')
    log.info(f'[SRV]          Server info is ({server_info})')
    log.info('-' * 84)

    log.info('Dumping records to store...')
    store.dump(end_time=end_time, has_failures=has_failures)
    log.info('-' * 84)

    log.info('OK')
    log.info('=' * 84)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))  # pragma: no cover
