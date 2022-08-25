import copy
import datetime as dti
import json
import os
import pathlib
import re
import sys

APP_ALIAS = 'extract'
APP_ENV = APP_ALIAS.upper()
DEBUG = bool(os.getenv(f'{APP_ENV}_DEBUG', ''))
ENCODING = 'utf-8'

DB_PATH = pathlib.Path('db.json')

RECORD = re.compile(r'^(?P<timestamp>2[^ ]+) (?P<level>[^ ]+) \[(?P<app>[^[]+)\]: (?P<payload>.*)$')
START_PAYLOAD = re.compile(r'^# Starting 27-steps scenario test execution at (at )?\((?P<timestamp>[^)]+) UTC\)$')
NODE_PAYLOAD = re.compile(r'^- Setup <13> Node indicator \((?P<node>[^)]+)\)$')
SESSION_PAYLOAD = re.compile(
    r'^- Setup <14> Connect will be to upstream \(?(?P<mode>cloud|on-site|)\)? ?service \((?P<target>[^)]+)\)'
    r' per login \((?P<user>[^)]+)\)$'
)
END_PAYLOAD = re.compile(r'^# Ended execution of 27-steps scenario test at \((?P<timestamp>[^)]+) UTC\)$')
DURATION_PAYLOAD = re.compile(r'^Execution of 27-steps scenario test took (?P<duration>[^ ]+) h:mm:ss.uuuuuu$')
PARSE_DURATION = re.compile(r'^(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>[\.\d]+)')

TS_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
ITS_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
XTS_FORMAT = '%Y%m%d%H%M%S.%f'


def load(db_path: pathlib.Path = DB_PATH):
    """Read events dict from the database if present otherwise provide empty dict.

    'scenario': [
        {
            'time_marker': 20220812090322.383,
            'start_ts': '2022-08-12 09:03:22.382996',
            'end_ts': '2022-08-12 09:03:27.351715',
            'duration_s': 4.968719,
            'rank_local': 1,
            'node_indicator': '7430eea0-7599-37db-b782-bbd336e7a755',
            'mode': '',
            'target': 'https://jiraabcd.example.com',
            'user_id': 'userid',
            'session_ts': '2022-08-12 09:03:22.382996',
            'location_path': 'str-path-log-file',
        }
    ]

    """
    if db_path.is_file() and db_path.stat().st_size:
        with open(db_path, 'rt', encoding=ENCODING) as handle:
            return json.load(handle)
    else:
        return {}


def dump(events, db_path: pathlib.Path = DB_PATH):
    """Dump the events dict to the database."""
    with open(db_path, 'wt', encoding=ENCODING) as handle:
        json.dump(events, handle)


def slugify_target(text):
    """Valid file name part from URL."""
    return text.strip().split('//')[1].split('.')[0]


def main(argv=None):
    """Extract the log duration and attributes into a JSON database."""
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print('usage: extract.py log-file-glob')
        return 2

    events = load(DB_PATH)
    ranks = {}
    locations_known = []
    for scenario, data in events.items():
        for event in data:
            ranks[scenario] = event['rank_local']
            locations_known.append(event['location_path'])
    visited = set(locations_known)

    for location in sorted(loc for loc in argv if loc not in visited):
        DEBUG and print(f'Processing {location}')
        path = pathlib.Path(location)
        scenario = str(path.parent)
        if scenario not in ranks:
            ranks[scenario] = 0
        ranks[scenario] += 1
        if scenario not in events:
            events[scenario] = []
        end_ts = None
        duration_value = None
        with open(path, 'rt', encoding=ENCODING) as handle:
            for line in handle:
                match = RECORD.match(line)
                if match:
                    record = copy.deepcopy(match.groupdict())
                    start_match = START_PAYLOAD.match(record['payload'])
                    if start_match:
                        start = copy.deepcopy(start_match.groupdict())
                        start_ts = dti.datetime.strptime(start['timestamp'], ITS_FORMAT)
                        continue
                    node_match = NODE_PAYLOAD.match(record['payload'])
                    if node_match:
                        node = copy.deepcopy(node_match.groupdict())
                        node_indicator = node['node']
                        continue
                    session_match = SESSION_PAYLOAD.match(record['payload'])
                    if session_match:
                        session = copy.deepcopy(session_match.groupdict())
                        mode = session['mode']
                        target = session['target']
                        user = session['user']
                        # session_ts = dti.datetime.strptime(session['timestamp'], ITS_FORMAT)
                        continue
                    end_match = END_PAYLOAD.match(record['payload'])
                    if end_match:
                        end = copy.deepcopy(end_match.groupdict())
                        end_ts = dti.datetime.strptime(end['timestamp'], ITS_FORMAT)
                        continue
                    duration_match = DURATION_PAYLOAD.match(record['payload'])
                    if duration_match:
                        duration = copy.deepcopy(duration_match.groupdict())
                        parts = PARSE_DURATION.match(duration['duration'])
                        time_params = {name: float(param) for name, param in parts.groupdict().items() if param}
                        duration_value = dti.timedelta(**time_params)
                        continue

        events[scenario].append(
            {
                'time_marker': round(float(start_ts.strftime(XTS_FORMAT)), 3),
                'start_ts': start_ts.strftime(ITS_FORMAT),
                'end_ts': end_ts.strftime(ITS_FORMAT) if end_ts else start_ts.strftime(ITS_FORMAT),
                'duration_s': duration_value.total_seconds() if duration_value else None,
                'rank_local': ranks[scenario],
                'node_indicator': node_indicator,
                'mode': mode,
                'target': target,
                'user_id': user,
                'session_ts': start_ts.strftime(ITS_FORMAT),  # session_ts.strftime(ITS_FORMAT),
                'location_path': location,
            }
        )

    dump(events, DB_PATH)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
