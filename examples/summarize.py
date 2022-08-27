import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(color_codes=True)  # style="whitegrid")
pd.options.display.width = None

APP_ALIAS = 'summarize'
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
A_SECOND_OF_USECS = 1_000_000

scenario_labels_sequence = (  # Labels in scenario order:
    'LOGIN',
    'SERVER_INFO',
    'PROJECTS',
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

atomic_labels_set = set(sorted(scenario_labels_sequence))

node_map = {
    '5c53f0de-8417-33df-9db8-718895b1f786': 'wun',
    '1c2175b4-eec5-3536-be76-2f20865df8ae': 'two',
    '7430eea0-7599-37db-b782-bbd336e7a755': 'thr',
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
            tmp_df = df[
                df['target_alias'].isin([node]) & df['scenario'].isin(['single']) & df['step_label'].isin([transaction])
            ]
            print(
                tmp_df[
                    [
                        'total_secs',
                        'transactions_secs',
                        'duty_cycle_percent',
                        'step_dt_usecs',
                        'gap_before_millis',
                        'gap_after_millis',
                    ]
                ].describe()
            )
            print('-' * 42)
            print()

    print(
        f'{scenario_count} {steps_per_scenario}-step scenarios collected for {len(targets)}'
        f' distinct targets with a total of {step_count} measurements'
    )

    group = {
        'all': sorted(atomic_labels_set),
        'read': sorted(['SERVER_INFO', 'PROJECTS', 'ISSUE_EXISTS', 'EXECUTE_JQL', 'GET_ISSUE_STATUS', 'LOAD_ISSUE']),
        'write': sorted(
            [
                'LOGIN',
                'CREATE_ISSUE',
                'AMEND_ISSUE_DESCRIPTION',
                'ADD_COMMENT',
                'UPDATE_ISSUE_FIELD',
                'CREATE_DUPLICATES_LINK',
                'SET_ISSUE_STATUS',
                'SET_ORIGINAL_ESTIMATE',
                'CREATE_COMPONENT',
                'RELATE_ISSUE_TO_COMPONENT',
            ]
        ),
        **{label: [label] for label in sorted(atomic_labels_set)},
    }
    node_col = 'target_alias'
    y_col = 'step_dt_usecs'
    x_col = 'step_start_rel_float_epoc'
    sel_col = 'step_label'
    describe_these = [
        'total_secs',
        'transactions_secs',
        'duty_cycle_percent',
        y_col,
        'gap_before_millis',
        'gap_after_millis',
    ]
    # rescale expired secods to expired hours:
    df[[x_col]] /= 3600.0
    x_max = int(df[x_col].max()) + 1
    y_max = max(int(df[y_col].max()) + 1, A_SECOND_OF_USECS)
    for node in targets:
        print(node)
        node_df = df[df[node_col].isin([node])]
        for name, labels in group.items():
            print(f'- selector({name}):')
            sel_df = node_df[node_df[sel_col].isin(labels)]
            print(sel_df[describe_these].describe())
            print('-' * 42)
            print()

            parameters = dict(
                x=x_col,
                y=y_col,
                hue=sel_col,
                hue_order=labels,
                data=sel_df,
                robust=True,
                ci=95,
                markers='o',
                palette='deep',
                scatter_kws={'s': 3},
                facet_kws={'legend_out': True},
                legend=True,
            )
            g = sns.lmplot(**parameters)
            # check axes and find which is have legend
            for ax in g.axes.flat:
                leg = g.axes.flat[0].get_legend()
                if leg is not None:
                    break
            # or legend may be on a figure
            if leg is None:
                leg = g._legend
            leg.set_title('Action')
            # handles, p_lables = g.get_legend_handles_labels()
            # for h in handles:
            #    h.set_markersize(10)
            # # replace legend using handles and labels from above
            # lgnd = plt.legend(handles, p_lables, bbox_to_anchor=(1.02, 0.5), loc='upper center', borderaxespad=0,
            #                   title='Actions')
            fig = g.fig
            axes = plt.gca()
            axes.set_ylim([0, y_max])
            if name == 'LOGIN':
                axes.set_ylim([0, 1000])
            axes.set_xlim([0, x_max])
            axes.yaxis.grid(True)
            axes.xaxis.grid(True)
            axes.set_ylabel('dt[µs]')
            axes.set_xlabel('Relative start time during campaign [h]')
            # lgnd = plt.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0, title='Action',
            #                                   scatterpoints=1, fontsize=8)
            # for handle in lgnd.legendHandles:
            #     handle.set_sizes([8.0])

            fig.savefig(f'timeseries-{name}-{node}.svg', format='svg')
            fig.savefig(f'timeseries-{name}-{node}.png', format='png')
            DEBUG and plt.show()
            plt.close()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
