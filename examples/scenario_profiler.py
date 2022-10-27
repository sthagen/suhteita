#! /usr/bin/env python
"""Profile the scenario data to prepare graphing and root cause analysis."""
import copy
import datetime as dti
import glob
import json
import pathlib
import sys
from typing import Any

ENCODING = 'utf-8'
HALF_SECOND_OF_USECS = 500_000
SLOWNESS_SECS = 3 * HALF_SECOND_OF_USECS / 1_000_000
SCENARIOS = ('single', 'twins')
PARSE_TS_FORMAT = '%Y-%m-%d %H:%M:%S.%f UTC'
STEP_TA_MAP = {
    1: 'LOGIN',
    2: 'SERVER_INFO',
    3: 'PROJECTS',
    4: 'CREATE_ISSUE',
    5: 'ISSUE_EXISTS',
    6: 'CREATE_ISSUE',
    7: 'ISSUE_EXISTS',
    8: 'EXECUTE_JQL',
    9: 'AMEND_ISSUE_DESCRIPTION',
    10: 'ADD_COMMENT',
    11: 'UPDATE_ISSUE_FIELD',
    12: 'UPDATE_ISSUE_FIELD',
    13: 'CREATE_DUPLICATES_ISSUE_LINK',
    14: 'GET_ISSUE_STATUS',
    15: 'SET_ISSUE_STATUS',
    16: 'SET_ISSUE_STATUS',
    17: 'GET_ISSUE_STATUS',
    18: 'ADD_COMMENT',
    19: 'SET_ORIGINAL_ESTIMATE',
    20: 'GET_ISSUE_STATUS',
    21: 'SET_ISSUE_STATUS',
    22: 'GET_ISSUE_STATUS',
    23: 'CREATE_COMPONENT',
    24: 'RELATE_ISSUE_TO_COMPONENT',
    25: 'LOAD_ISSUE',
    26: 'ADD_COMMENT',
    27: 'ADD_COMMENT',
}

TA_MMAP = {
    'LOGIN': [1],
    'SERVER_INFO': [2],
    'PROJECTS': [3],
    'CREATE_ISSUE': [4, 6],
    'ISSUE_EXISTS': [5, 7],
    'EXECUTE_JQL': [8],
    'AMEND_ISSUE_DESCRIPTION': [9],
    'ADD_COMMENT': [10, 18, 26, 27],
    'UPDATE_ISSUE_FIELD': [11, 12],
    'CREATE_DUPLICATES_ISSUE_LINK': [13],
    'GET_ISSUE_STATUS': [14, 17, 20, 22],
    'SET_ISSUE_STATUS': [15, 16, 21],
    'SET_ORIGINAL_ESTIMATE': [19],
    'CREATE_COMPONENT': [23],
    'RELATE_ISSUE_TO_COMPONENT': [24],
    'LOAD_ISSUE': [25],
}

ReportDict = dict[int | str, float | int | str | dict[int | str, float | int | str | Any | Any]]
benchmark: dict[str, int | str | list[int, float, str] | ReportDict] = {
    'ts_frame_start': None,
    'ts_frame_end': None,
    'sequence_count': 0,
    'slow_ta_count': 0,
    'total_ta_count': 0,
    'sequence_ok_count': 0,
    'ta_ok_count': 0,
    'slow_means_more_than_secs': SLOWNESS_SECS,
    'step_to_ta': copy.deepcopy(STEP_TA_MAP),
    'ta_mmap': copy.deepcopy(TA_MMAP),
    'probes': {},
    'targets': {},
}
for path in sorted(glob.glob(sys.argv[1])):
    with open(path, 'rt', encoding=ENCODING) as handle:
        profile = json.load(handle)

    meta = profile['_meta']

    scenario = meta['scenario']
    flavor = meta['identity']
    mode = meta['mode']
    probe = meta['node_indicator'].split('-', 1)[0]
    target = meta['target'].split('https://')[1].split('.', 1)[0].lower()
    if '-' in target:
        target = target.split('-')[-1]
    else:
        target = target.replace('jiraabcd', 'prod')
    if target == '154':
        target = 'cloud-prod'
    elif target == 'dilettant':
        target = 'cloud-ref'

    ok = not (meta['has_failures_declared'] or meta['has_failures_detected'])
    start_ts_str = meta['start_ts']
    total_start_ts = dti.datetime.strptime(start_ts_str, PARSE_TS_FORMAT)
    end_ts_str = meta['end_ts']
    total_secs = meta['total_secs']

    if probe not in benchmark['probes']:
        benchmark['probes'][probe] = meta['node_indicator']
    if target not in benchmark['targets']:
        benchmark['targets'][target] = {
            'probes': [],
            'scenarios': [],
            'flavors': [],
            'first_start_ts': start_ts_str,
            'last_end_ts': end_ts_str,
            'sequence_count': 0,
            'slow_ta_count': 0,
            'total_ta_count': 0,
            'sequence_ok_count': 0,
            'ta_ok_count': 0,
            'zip_me_start_ts': [],
            'zip_me_end_ts': [],
            'total_secs': [],
            'duty_secs': [],
            'duty_cycles_percent': [],
            'slow_transactions': []
        }

    events = profile['events']

    report: dict[str, float | int | str | Any] = {
        'scenario': scenario,
        'probe': probe,
        'target': target,
        'ok': ok,
        'start_ts': start_ts_str,
        'end_ts': end_ts_str,
        'total_secs': total_secs,
        'duty_secs': 0,
        'duty_cycle_percent': 0,
        'trace': [],
    }

    duty_secs = 0
    for event in events:
        rank = event['rank']
        label = event['label']
        ok = event['ok']
        start_ts = dti.datetime.strptime(event['start_ts'], PARSE_TS_FORMAT)
        end_ts = dti.datetime.strptime(event['end_ts'], PARSE_TS_FORMAT)
        start_rel = start_ts - total_start_ts
        end_rel = end_ts - total_start_ts
        step_dt = end_ts - start_ts
        # duration_usecs = event['duration_usecs']
        dt_usecs = 1_000_000 * step_dt.seconds + step_dt.microseconds
        duty_secs += dt_usecs
        report['trace'].append(
            {
                'step': rank,
                'label': label,
                'duration_usecs': dt_usecs,
                'ok': ok,
                'start_rel': start_rel.total_seconds(),
                'start_ts': event['start_ts'],
                'end_rel': end_rel.total_seconds(),
            }
        )
    report['duty_secs'] = duty_secs / 1.e6
    duty_cycle_percent = 100 * report['duty_secs'] / total_secs
    report['duty_cycle_percent'] = duty_cycle_percent

    if probe not in benchmark['targets'][target]['probes']:
        benchmark['targets'][target]['probes'].append(probe)
    if scenario not in benchmark['targets'][target]['scenarios']:
        benchmark['targets'][target]['scenarios'].append(scenario)
    if flavor not in benchmark['targets'][target]['flavors']:
        benchmark['targets'][target]['flavors'].append(flavor)

    if benchmark['ts_frame_start'] is None:
        benchmark['ts_frame_start'] = start_ts_str
        benchmark['ts_frame_end'] = end_ts_str
    else:
        if start_ts_str < benchmark['ts_frame_start']:
            benchmark['ts_frame_start'] = start_ts_str
        if benchmark['ts_frame_end'] < end_ts_str:
            benchmark['ts_frame_end'] = end_ts_str

    if start_ts_str < benchmark['targets'][target]['first_start_ts']:
        benchmark['targets'][target]['first_start_ts'] = start_ts_str
    if benchmark['targets'][target]['last_end_ts'] < end_ts_str:
        benchmark['targets'][target]['last_end_ts'] = end_ts_str

    benchmark['targets'][target]['sequence_count'] += 1
    benchmark['targets'][target]['sequence_ok_count'] += 1 if ok else 0
    benchmark['targets'][target]['zip_me_start_ts'].append(start_ts_str)
    benchmark['targets'][target]['zip_me_end_ts'].append(end_ts_str)
    benchmark['targets'][target]['total_secs'].append(total_secs)
    benchmark['targets'][target]['duty_secs'].append(report['duty_secs'])
    benchmark['targets'][target]['duty_cycles_percent'].append(report['duty_cycle_percent'])
    benchmark['targets'][target]['total_ta_count'] += len(report['trace'])

    benchmark['sequence_count'] += 1
    benchmark['total_ta_count'] += len(report['trace'])
    benchmark['sequence_ok_count'] += 1 if ok else 0

    for event in report['trace']:
        if event['ok']:
            benchmark['targets'][target]['ta_ok_count'] += 1
            benchmark['ta_ok_count'] += 1
        if event['duration_usecs'] < SLOWNESS_SECS * 1_000_000:
            continue
        benchmark['targets'][target]['slow_ta_count'] += 1
        benchmark['slow_ta_count'] += 1
        slot = len(benchmark['targets'][target]['slow_transactions'])
        benchmark['targets'][target]['slow_transactions'].append(
            {
                'slot': slot + 1,  # we start at 1
                'ta_secs': event['duration_usecs'] / 1_000_000,
                'label': event['label'],
                'step': event['step'],
                'day_tag': total_start_ts.strftime('%Y-%m-%d'),
                'month_tag': total_start_ts.strftime('%Y-%m'),
                'year': total_start_ts.year,
                'sequence_start_ts': start_ts_str,
                'event_start_ts': event['start_ts'],
                'start_rel': event['start_rel'],
                'end_rel': event['end_rel'],
                'scenario': scenario,
                'flavor': flavor,
            }
        )

    print(file=sys.stderr)
    print(
        f'{scenario}:{probe} -> {target} => {total_secs :5.2f} secs duration ({duty_cycle_percent :.3f}% duty-cycle)'
        f' started {start_ts_str} and status {"OK" if ok else "FAIL"}',
        file=sys.stderr)
    print(file=sys.stderr)
    for event in report['trace']:
        step = event['step']
        label = event['label']
        duration_usecs = event['duration_usecs']
        ok = event['ok']
        start_rel = event['start_rel']
        end_rel = event['end_rel']
        alert = '' if duration_usecs < HALF_SECOND_OF_USECS else f' {"*" * (duration_usecs // HALF_SECOND_OF_USECS)}'
        print(
            f'- {step :2d}: {start_rel :6.3f} -> {end_rel :6.3f} [{duration_usecs :8d} usecs] for {label :28}{alert}',
            file=sys.stderr
        )

    report_name = pathlib.Path(path).name
    with open(pathlib.Path(pathlib.Path('out') / report_name), 'wt', encoding=ENCODING) as handle:
        json.dump(report, handle, indent=2)

with open(pathlib.Path('out') / 'benchmark.json', 'wt', encoding=ENCODING) as handle:
    json.dump(benchmark, handle, indent=2)

total_seq_count = benchmark['sequence_count']
seq_ok = benchmark['sequence_ok_count']
total_ta_count = benchmark['total_ta_count']
tas_ok = benchmark['ta_ok_count']
slow_ta_count = benchmark['slow_ta_count']
probes_count = len(benchmark["probes"])
rep_start = benchmark['ts_frame_start']
rep_end = benchmark['ts_frame_end']
rep_start_date = rep_start[:10]
rep_end_date = rep_end[:10]
interval = rep_start_date if rep_start_date == rep_end_date else f'{rep_start_date} - {rep_end_date}'
print()
print(f'# Report {interval}')
print()
print(f'Time frame of the report is from {rep_start} through {rep_end}.')
print()
print(
    f'{probes_count} probe{"" if probes_count == 1 else "s"} executed in total {total_seq_count} successful sequences'
    f' with {total_ta_count} total transactions probing {len(benchmark["targets"])} different JIRA instances.'
)
print(
    f'{seq_ok} of the {total_seq_count} total sequences (runs) and'
    f' {tas_ok} of the {total_ta_count} total transactions were valid.'
)
print(
    f'{slow_ta_count} of the {total_ta_count} total transactions were rated as slow'
    f' (taking longer than {benchmark["slow_means_more_than_secs"]} seconds).'
)
print()

print('## Targets')
targets = sorted(target for target in benchmark['targets'])
for target in targets:
    tg = benchmark['targets'][target]
    tg_start = tg['first_start_ts']
    tg_end = tg['last_end_ts']
    tg_sequence_count = tg['sequence_count']
    tg_slow_ta_count = tg['slow_ta_count']
    tg_total_ta_count = tg['total_ta_count']
    tg_sequence_ok_count = tg['sequence_ok_count']
    tg_ta_ok_count = tg['ta_ok_count']
    tg_probes_count = len(tg['probes'])
    print()
    print(f'### JIRA Instance - {target}')
    print()
    print(f'Time frame of the report for the {target} instance is from {tg_start} through {tg_end}.')
    print()
    print(
        f'{tg_probes_count} probe{"" if tg_probes_count == 1 else "s"} executed in'
        f' total {tg_sequence_count} successful sequences'
        f' with {tg_total_ta_count} total transactions probing the {target} JIRA instance.'
    )
    print(
        f'{tg_sequence_ok_count} of the {tg_sequence_count} total sequences (runs) and'
        f' {tg_ta_ok_count} of the {tg_total_ta_count} total transactions were valid.'
    )
    print(
        f'{tg_slow_ta_count} of the {tg_total_ta_count} total transactions were rated as slow'
        f' (taking longer than {benchmark["slow_means_more_than_secs"]} seconds).'
    )
print()
