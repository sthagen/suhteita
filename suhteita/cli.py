#! /usr/bin/env python
"""CLI operations for relationships (Finnish: suhteita) maintained across distances as load test core."""
import argparse
import sys
from typing import List, Union

import suhteita.suhteita as api
from suhteita import APP_ALIAS, APP_ENV, BASE_URL, IDENTITY, IS_CLOUD, PROJECT, STORE, USER


def parse_request(argv: List[str]) -> argparse.Namespace:
    """DRY."""
    parser = argparse.ArgumentParser(description=APP_ALIAS)
    parser.add_argument(
        '--user',
        '-u',
        dest='user',
        default=USER,
        help=f'user (default: {USER if USER else f"None, set {APP_ENV}_USER for default"})',
    )
    parser.add_argument(
        '--target',
        '-t',
        dest='target_url',
        default=BASE_URL,
        help=f'target URL (default: {BASE_URL if BASE_URL else f"None, set {APP_ENV}_BASE_URL for default"})',
    )
    parser.add_argument(
        '--is-cloud',
        action='store_true',
        dest='is_cloud',
        default=IS_CLOUD,
        help=(
            'target is cloud instance (default: '
            f'{"True" if IS_CLOUD else f"False, set {APP_ENV}_IS_CLOUD for a different default"})'
        ),
    )
    parser.add_argument(
        '--project',
        '-p',
        dest='target_project',
        default=PROJECT,
        help=f'target project (default: {PROJECT if PROJECT else f"None, set {APP_ENV}_PROJECT for default"})',
    )
    parser.add_argument(
        '--scenario',
        '-s',
        dest='scenario',
        default='unknown',
        help='scenario for recording (default: unknown)',
    )
    parser.add_argument(
        '--identity',
        '-i',
        dest='identity',
        default=IDENTITY if IDENTITY else 'adhoc',
        help=(
            'identity of take for recording'
            f' (default: {IDENTITY if IDENTITY else f"adhoc, set {APP_ENV}_IDENTITY for default"})'
        ),
    )
    parser.add_argument(
        '--out-path',
        '-o',
        dest='out_path',
        default=STORE if STORE else 'store',
        help=(
            'output folder path for recording'
            f' (default: {STORE if STORE else f"store, set {APP_ENV}_STORE for default"})'
        ),
    )
    return parser.parse_args(argv)


# pylint: disable=expression-not-assigned
def main(argv: Union[List[str], None] = None) -> int:
    """Delegate processing to functional module."""
    argv = sys.argv[1:] if argv is None else argv

    return api.main(parse_request(argv))
