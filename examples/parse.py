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

RECORD = re.compile(r'^(?P<timestamp>2[^ ]+) (?P<level>[^ ]+) \[(?P<app>[^[]+)\]: (?P<payload>.*)$')
START_PAYLOAD = re.compile(r'^Starting load test execution at (at )?\((?P<timestamp>[^)]+) UTC\)$')
NODE_PAYLOAD = re.compile(r'^Node indicator \((?P<node>[^)]+)\)$')
SESSION_PAYLOAD = re.compile(
    r'^Connecting to upstream \(?(?P<mode>cloud|on-site|)\)? ?service \((?P<target>[^)]+)\)'
    r' per login \((?P<user>[^)]+)\) at \((?P<timestamp>[^)]+) UTC\)$'
)
END_PAYLOAD = re.compile(r'^Ended execution of load test at \((?P<timestamp>[^)]+) UTC\)$')
DURATION_PAYLOAD = re.compile(r'^Execution of load test took (?P<duration>[^ ]+) h:mm:ss.uuuuuu$')
PARSE_DURATION = re.compile(r'^(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>[\.\d]+)')

TS_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
ITS_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
XTS_FORMAT = '%Y%m%d%H%M%S.%f'


def main(argv=None):
    """Extract the log duration and attributes into a JSON database."""
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print('usage: parse_proto.py log-file-glob')
        sys.exit(2)

    locations = sorted(argv)
    events = {}
    ranks = {}
    for location in locations:
        path = pathlib.Path(location)
        parent = str(path.parent)
        if parent not in ranks:
            ranks[parent] = 0
        ranks[parent] += 1
        if parent not in events:
            events[parent] = []
        with open(path, 'rt', encoding=ENCODING) as handle:
            DEBUG and print(f'from: {path}')
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
                        session_ts = dti.datetime.strptime(session['timestamp'], ITS_FORMAT)
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

        events[parent].append(
            [
                round(float(start_ts.strftime(XTS_FORMAT)), 3),
                start_ts.strftime(ITS_FORMAT),
                end_ts.strftime(ITS_FORMAT),
                duration_value.total_seconds(),
                ranks[parent],
                node_indicator,
                mode,
                target,
                user,
                session_ts.strftime(ITS_FORMAT),
            ]
        )

    with open('parsed.json', 'wt', encoding=ENCODING) as handle:
        json.dump(events, handle, indent=2)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
