"""creator store grep."""
import datetime as dti
import json
import pathlib
import sys

import pandas as pd

pd.options.display.width = None

scenario_labels_sequence = (  # Labels in scenario order:
    'LOGIN',
    'SERVER_INFO',
    'PROJECTS',
    'CREATE_ISSUE',
)
scenario_labels_set = set(sorted(scenario_labels_sequence))

node_map = {
    '5c53f0de-8417-33df-9db8-718895b1f786': 'wun',
    '1c2175b4-eec5-3536-be76-2f20865df8ae': 'two',
    '7430eea0-7599-37db-b782-bbd336e7a755': 'the',
    'c79891e5-aabf-3a83-95b9-588edcd8327f': 'mountain',
}
target_aliases = ('cloud-ref', 'cloud-prod', 'prod', 'test')

ENCODING = 'utf-8'

UTC_TS_FORMAT = '%Y-%m-%d %H:%M:%S.%f UTC'
FAR_FUTURE = '3000-08-13 11:32:26.250224 UTC'
LONG_PAST = '1000-08-13 11:32:26.250224 UTC'

if len(sys.argv) < 2:
    print('usage: cstrep file(s)')
    sys.exit(2)

profiles = []
nodes = {}
targets = set()
for name in sys.argv[1:]:
    path = pathlib.Path(name)
    with open(path, 'rt', encoding=ENCODING) as handle:
        db = json.load(handle)
    scenario = db['_meta']['scenario']
    target_class = db['_meta']['mode']
    client_node_id = db['_meta']['node_indicator']
    client_alias = node_map.get(client_node_id, 'UNKNOWN')
    if client_alias not in nodes:
        nodes[client_alias] = 0

    nodes[client_alias] += 1
    identity = db['_meta']['identity']
    target_alias, split_id = identity.split('-', 1)[1].rsplit('-', 1)
    if target_alias not in targets:
        targets.add(target_alias)
    start_ts = db['_meta']['start_ts']
    start_time = dti.datetime.strptime(start_ts, UTC_TS_FORMAT)

    total_secs = db['_meta']['total_secs']
    end_ts = db['_meta']['end_ts']
    end_time = dti.datetime.strptime(end_ts, UTC_TS_FORMAT)

    logins = [event for event in db['events'] if event['label'] == 'LOGIN']
    creates_of_issue = [event for event in db['events'] if event['label'] == 'CREATE_ISSUE']
    loads_of_issue = [event for event in db['events'] if event['label'] == 'LOAD_ISSUE']
    adds_of_comment = [event for event in db['events'] if event['label'] == 'ADD_COMMENT']
    gets_of_issue_status = [event for event in db['events'] if event['label'] == 'GET_ISSUE_STATUS']
    sets_of_issue_status = [event for event in db['events'] if event['label'] == 'SET_ISSUE_STATUS']

    print(f'db({name}):')
    print(f'- {identity=}')
    print(f'- {start_ts=}')
    print(f'- {total_secs=}')

    print('- logins:')
    for login in logins:
        ok = '' if login['ok'] else ' (FAIL)'
        print(f'  + dt = {login["duration_usecs"]} usecs{ok}')

    print('- creates of issue:')
    for create_issue in creates_of_issue:
        ok = '' if create_issue['ok'] else ' (FAIL)'
        print(f'  + dt = {create_issue["duration_usecs"]} usecs{ok}')

    print('- loads of issue:')
    for load_issue in loads_of_issue:
        ok = '' if load_issue['ok'] else ' (FAIL)'
        print(f'  + dt = {load_issue["duration_usecs"]} usecs{ok}')

    print('- adds of comment:')
    for add_comment in adds_of_comment:
        ok = '' if add_comment['ok'] else ' (FAIL)'
        print(f'  + dt = {add_comment["duration_usecs"]} usecs{ok}')

    print('- gets of issue status:')
    for get_issue_status in gets_of_issue_status:
        ok = '' if get_issue_status['ok'] else ' (FAIL)'
        print(f'  + dt = {get_issue_status["duration_usecs"]} usecs{ok}')

    print('- sets of issue status:')
    for set_issue_status in sets_of_issue_status:
        ok = '' if set_issue_status['ok'] else ' (FAIL)'
        print(f'  + dt = {set_issue_status["duration_usecs"]} usecs{ok}')
    print(f'- {end_ts=}')

    print('- profile:')
    steps_profile = []
    ta_usecs = 0
    steps = [event for event in db['events']]
    end_step_trigger = len(steps)
    previous_start_time = start_time
    for order, step in enumerate(steps, start=1):
        label = step['label']
        comment = step['comment']
        step_start_ts = step['start_ts']
        step_end_ts = step['end_ts']
        # dt_usecs = step['duration_usecs']
        step_start_time = dti.datetime.strptime(step_start_ts, UTC_TS_FORMAT)
        step_end_time = dti.datetime.strptime(step_end_ts, UTC_TS_FORMAT)
        dt = step_end_time - step_start_time
        dt_usecs = 1_000_000 * dt.seconds + dt.microseconds
        dt_secs = dt_usecs / 1.0e6
        ta_usecs += dt_usecs
        ok = '      ' if step['ok'] else '(FAIL)'
        status = 'SUCC' if step['ok'] else 'FAIL'

        step_start_time = dti.datetime.strptime(step_start_ts, UTC_TS_FORMAT)
        step_end_time = dti.datetime.strptime(step_end_ts, UTC_TS_FORMAT)
        gap_before_millis = round(1.0e3 * (step_start_time - previous_start_time).total_seconds(), 3)
        previous_start_time = step_end_time
        if order == end_step_trigger:
            gap_after_millis = round(1.0e3 * (end_time - step_end_time).total_seconds(), 3)
        else:
            peek_next_step_start_ts = steps[order]['start_ts']
            peek_next_step_start_time = dti.datetime.strptime(peek_next_step_start_ts, UTC_TS_FORMAT)
            gap_after_millis = round(1.0e3 * (peek_next_step_start_time - step_end_time).total_seconds(), 3)

        if order == 1:
            print(f'      gap before  {gap_before_millis :7.3f} millisecs')
        print(f'  {order :2d}: {dt_usecs :7d} {step_start_ts} {label :32s} {ok} {comment}')
        if order == end_step_trigger:
            print(f'      gap after   {gap_after_millis :7.3f} millisecs')
        else:
            print(f'      gap between {gap_after_millis :7.3f} millisecs')
        steps_profile.append(
            [
                order,
                step_start_ts,
                step_end_ts,
                dt_usecs,
                dt_secs,
                gap_before_millis,
                gap_after_millis,
                label,
                status,
                comment,
            ]
        )
    print(f'transaction_secs = {round(ta_usecs / 1.e6, 3)} secs')
    print(f'duty_cycle_percent = {round(100. * (ta_usecs / 1.e6) / total_secs, 3)} %')
    print('-' * 42)
    ta_secs = ta_usecs / 1.0e6
    dc_percent = round(100.0 * ta_secs / total_secs, 3)
    for (
        order,
        step_start_ts,
        step_end_ts,
        dt_usecs,
        dt_secs,
        gap_before_millis,
        gap_after_millis,
        label,
        status,
        comment,
    ) in steps_profile:
        profiles.append(
            {
                'scenario': scenario,
                'sub_scenario': split_id,
                'identity': identity,
                'client_node_id': client_node_id,
                'client_alias': client_alias,
                'target_alias': target_alias,
                'target_class': target_class,
                'start_ts': start_ts,
                'start_rel_float_epoc': None,  # relative epoc from min of all registered start times
                'end_ts': end_ts,
                'end_rel_float_epoc': None,  # dito
                'total_secs': total_secs,
                'transactions_secs': ta_secs,
                'duty_cycle_percent': dc_percent,
                'sub_transaction': order,
                'step_start_ts': step_start_ts,
                'step_start_rel_float_epoc': None,  # dito
                'step_end_ts': step_end_ts,
                'step_end_rel_float_epoc': None,  # dito
                # below sub_trans... = 100 * (step_start - ta_start).total_seconds() / total_secs
                'sub_transaction_local_start_rel_float_percent': None,
                'step_dt_usecs': dt_usecs,
                'step_dt_secs': dt_secs,
                'gap_before_millis': gap_before_millis,
                'gap_after_millis': gap_after_millis,
                'step_label': label,
                'step_status': status,
                'step_comment': comment,
            }
        )

early_ts, late_ts = FAR_FUTURE, LONG_PAST
early_ts = min(FAR_FUTURE, *[step['start_ts'] for step in profiles])
late_ts = max(LONG_PAST, *[step['end_ts'] for step in profiles])

early_time = dti.datetime.strptime(early_ts, UTC_TS_FORMAT)
late_time = dti.datetime.strptime(late_ts, UTC_TS_FORMAT)
print(early_ts, late_ts)
print(early_time, late_time)

period = late_time - early_time
print(f'{period=}')
period_secs = period.total_seconds()
print(f'{period_secs}')

for k, profile in enumerate(profiles):
    ta_start_ts = profile['start_ts']
    ta_start_time = dti.datetime.strptime(ta_start_ts, UTC_TS_FORMAT)
    ta_end_ts = profile['end_ts']
    ta_end_time = dti.datetime.strptime(ta_end_ts, UTC_TS_FORMAT)
    sta_start_ts = profile['step_start_ts']
    sta_start_time = dti.datetime.strptime(sta_start_ts, UTC_TS_FORMAT)
    sta_end_ts = profile['step_end_ts']
    sta_end_time = dti.datetime.strptime(sta_end_ts, UTC_TS_FORMAT)
    total_secs = profile['total_secs']
    profiles[k]['start_rel_float_epoc'] = (ta_start_time - early_time).total_seconds()
    profiles[k]['end_rel_float_epoc'] = (ta_end_time - early_time).total_seconds()
    profiles[k]['step_start_rel_float_epoc'] = (sta_start_time - early_time).total_seconds()
    profiles[k]['step_end_rel_float_epoc'] = (sta_end_time - early_time).total_seconds()
    profiles[k]['sub_transaction_local_start_rel_float_percent'] = (
        100 * (sta_start_time - ta_start_time).total_seconds() / total_secs
    )

with open('creator-profiles.json', 'wt', encoding=ENCODING) as handle:
    json.dump(profiles, handle)

df = pd.DataFrame(profiles)
print(df.head())

for transaction in scenario_labels_set:
    for node in targets:
        print(node, transaction, '-' * 42)
        tmp_df = df[
            df['target_alias'].isin([node]) & df['scenario'].isin(['creator']) & df['step_label'].isin([transaction])
        ]
        print(
            tmp_df[
                [
                    'total_secs',
                    'transactions_secs',
                    'duty_cycle_percent',
                    'step_dt_secs',
                    'gap_before_millis',
                    'gap_after_millis',
                ]
            ].describe()
        )
        print('-' * 42)
        print()

print(nodes)

for node in targets:
    print(node)
    tmp_df = df[df['target_alias'].isin([node]) & df['scenario'].isin(['creator'])]
    print(
        tmp_df[
            [
                'total_secs',
                'transactions_secs',
                'duty_cycle_percent',
                'step_dt_secs',
                'gap_before_millis',
                'gap_after_millis',
            ]
        ].describe()
    )
    print('-' * 42)
    print()
