import json
import math
import os
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(color_codes=True)  # style="whitegrid")

APP_ALIAS = 'report'
APP_ENV = APP_ALIAS.upper()
DEBUG = bool(os.getenv(f'{APP_ENV}_DEBUG', ''))
ENCODING = 'utf-8'

TS_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
ITS_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
XTS_FORMAT = '%Y%m%d%H%M%S.%f'

FAR_FUTURE = '3000-08-13 11:32:26.250224'
LONG_PAST = '1000-08-13 11:32:26.250224'

SINGLE = 'single'
TWINS = 'twins'
CLOSE = 0.1

scenario_labels_sequence = (  # Labels in scenario order:
    'LOGIN',
    'SERVER_INFO',
    'PROJECTS',
    'CREATE_TWINS',  # get rid of this call and instead use the four atomic steps below (now sub atomic)
    'CREATE_ISSUE',
    'ISSUE_EXISTS',
    'CREATE_ISSUE',
    'ISSUE_EXISTS',
    'EXECUTE_JQL',
    'AMEND_ISSUE_DESCRIPTION',
    'ADD_COMMENT',
    'UPDATE_ISSUE_FIELD',
    'UPDATE_ISSUE_FIELD',
    'CREATE_DUPLICATES_ISSUE_LINK',
    'GET_ISSUE_STATUS',
    'SET_ISSUE_STATUS',
    'SET_ISSUE_STATUS',
    'GET_ISSUE_STATUS',
    'ADD_COMMENT',
    'SET_ORIGINAL_ESTIMATE',
    'GET_ISSUE_STATUS',
    'SET_ISSUE_STATUS',
    'GET_ISSUE_STATUS',
    'CREATE_COMPONENT',
    'RELATE_ISSUE_TO_COMPONENT',
    'LOAD_ISSUE',
    'ADD_COMMENT',
    'ADD_COMMENT',
)

"""
> jq . store/some-db.json | grep label | cut -f 2 -d: | tr '"' "'" | sort | uniq -c
      4  'ADD_COMMENT',
      1  'AMEND_ISSUE_DESCRIPTION',
      1  'CREATE_COMPONENT',
      1  'CREATE_DUPLICATES_ISSUE_LINK',
      2  'CREATE_ISSUE',
      1  'CREATE_TWINS',
      1  'EXECUTE_JQL',
      4  'GET_ISSUE_STATUS',
      2  'ISSUE_EXISTS',
      1  'LOAD_ISSUE',
      1  'LOGIN',
      1  'PROJECTS',
      1  'RELATE_ISSUE_TO_COMPONENT',
      1  'SERVER_INFO',
      3  'SET_ISSUE_STATUS',
"""
scenario_labels_set = set(sorted(scenario_labels_sequence))
molecules = ('CREATE_TWINS',)
atomic_labels_set = set([label for label in scenario_labels_set if label not in molecules])

node_map = {
    '5c53f0de-8417-33df-9db8-718895b1f786': 'wun',
    '1c2175b4-eec5-3536-be76-2f20865df8ae': 'two',
    '7430eea0-7599-37db-b782-bbd336e7a755': 'the',
    'c79891e5-aabf-3a83-95b9-588edcd8327f': 'mountain',
}
target_aliases = ('cloud-ref', 'cloud-prod', 'prod', 'test')


UTC_TS_FORMAT = '%Y-%m-%d %H:%M:%S.%f UTC'
FAR_FUTURE = '3000-08-13 11:32:26.250224 UTC'
LONG_PAST = '1000-08-13 11:32:26.250224 UTC'


def set_axis_style(ax, labels):
    """Nice scenario axis"""
    ax.xaxis.set_tick_params(direction='out')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks(np.arange(1, len(labels) + 1), labels=labels)
    ax.set_xlim(0.25, len(labels) + 0.75)
    ax.set_xlabel('Sample name')


def adjacent_values(vals, q1, q3):
    """Manage overlap."""
    upper_adjacent_value = q3 + (q3 - q1) * 1.5
    upper_adjacent_value = np.clip(upper_adjacent_value, q3, vals[-1])

    lower_adjacent_value = q1 - (q3 - q1) * 1.5
    lower_adjacent_value = np.clip(lower_adjacent_value, vals[0], q1)
    return lower_adjacent_value, upper_adjacent_value


def load_events(db_path='profiles.json'):
    """Read events from the database."""
    with open(db_path, 'rt', encoding=ENCODING) as handle:
        return json.load(handle)


def slugify_target(text):
    """Valid file name part from URL."""
    return text.strip().split('//')[1].split('.')[0]


def main(argv=None):
    """Drive the endeavor."""
    argv = sys.argv[1:] if argv is None else argv
    events = load_events(argv[0]) if argv else load_events()
    targets = set(sorted(ev['target_alias'] for ev in events))
    scenario_count = sum(1 if ev['sub_transaction'] == 1 else 0 for ev in events)
    step_count = len(events)
    steps_per_scenario = step_count // scenario_count
    if steps_per_scenario < step_count / scenario_count:
        print('Problem with scenario step counts (not balanced)')
    df = pd.DataFrame(events)
    print(df.head())

    for transaction in atomic_labels_set:
        for node in targets:
            print(node, transaction, '-' * 42)
            tmp_df = df[df['target_alias'].isin([node]) & df['scenario'].isin(['single']) & df['step_label'].isin([transaction])]
            print(tmp_df[['total_secs', 'transactions_secs', 'duty_cycle_percent', 'step_dt_secs', 'gap_before_millis', 'gap_after_millis']].describe())
            print('-' * 42)
            print()

    print(
        f'{scenario_count} {steps_per_scenario}-step scenarios collected for {len(targets)}'
        f' distinct targets with a total of {step_count} measurements'
    )

    for node in targets:
        print(node)
        tmp_df = df[df['target_alias'].isin([node]) & df['scenario'].isin(['single'])]
        print(tmp_df[['total_secs', 'transactions_secs', 'duty_cycle_percent', 'step_dt_secs', 'gap_before_millis', 'gap_after_millis']].describe())
        print('-' * 42)
        print()

    final_plot = sns.lmplot(
        x='step_start_rel_float_epoc',
        y='step_dt_secs',
        hue='step_label',
        data=df,
        robust=True,
        ci=95,
        markers='o',
        palette='deep',
        scatter_kws={'s': 3},
    )
    fig = final_plot.fig
    axes = plt.gca()
    # axes.set_ylim([y_plot_min, y_plot_max])
    axes.set_xlim([0, None])
    axes.yaxis.grid(True)
    axes.xaxis.grid(True)
    axes.set_ylabel('')
    axes.set_xlabel(f'Time')

    fig.savefig(f'timeseries-cloud-ref.svg', format='svg')
    fig.savefig(f'timeseries-cloud-ref.png', format='png')
    DEBUG and plt.show()
    plt.close()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
