import json
import math
import os
import pathlib
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(color_codes=True)  # style="whitegrid")

APP_ALIAS = 'analyze'
APP_ENV = APP_ALIAS.upper()
DEBUG = bool(os.getenv(f'{APP_ENV}_DEBUG', ''))
ENCODING = 'utf-8'

DB_PATH = pathlib.Path('db.json')

TS_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
ITS_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
XTS_FORMAT = '%Y%m%d%H%M%S.%f'

FAR_FUTURE = '3000-08-13 11:32:26.250224'
LONG_PAST = '1000-08-13 11:32:26.250224'

SINGLE = 'single'
TWINS = 'twins'
CLOSE = 0.1


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


def slugify_target(text):
    """Valid file name part from URL."""
    return text.strip().split('//')[1].split('.')[0]


def main(argv=None):
    """Drive the endeavor."""
    argv = sys.argv[1:] if argv is None else argv
    events = load(pathlib.Path(argv[0])) if argv else load()
    x_all, y_all, z_all = [], [], []
    early, late = FAR_FUTURE, LONG_PAST
    for aspect, events in events.items():
        early = min(early, *[ev['start_ts'] for ev in events])
        late = max(late, *[ev['end_ts'] for ev in events])
        for event in events:
            x_all.append(aspect)
            y_all.append(event['duration_s'])
            z_all.append(slugify_target(event['target']))

    targets = sorted(set(z_all))
    for target in targets:
        x = [val for val, tgt in zip(x_all, z_all) if tgt == target]
        y = [val for val, tgt in zip(y_all, z_all) if tgt == target]
        y_min = min(y)
        y_max = max(y)
        c_single = sum(1 for v in x if v == SINGLE)
        c_twins = sum(1 for v in x if v == TWINS)
        early = early.split('.')[0]
        late = late.split('.')[0]

        mpl.rcParams['lines.linewidth'] = 0.7
        fig, axes = plt.subplots()

        df = pd.DataFrame({'scenario': x, 'duration': y})
        dataset = df[df.scenario == SINGLE]['duration'].values, df[df.scenario == 'twins']['duration'].values
        options = {
            'showmeans': True,
            'showextrema': True,
            'showmedians': True,
            'quantiles': [[0.05, 0.10, 0.90, 0.95], [0.05, 0.10, 0.90, 0.95]],
            'bw_method': 0.1,
            'vert': True,
        }
        parts = axes.violinplot(dataset, **options)
        for pc in parts['bodies']:
            pc.set_facecolor('#ffaaaa')
            pc.set_edgecolor('black')
            pc.set_alpha(0.7)
        parts['bodies'][0].set_facecolor('#ccccff')
        axes.set_title(f'Performance of service {target}\n[{early}, {late}]')
        axes.yaxis.grid(True)
        axes.set_ylabel(f'Time [s] for {target}')
        labels = [f'{SINGLE.title()}(n={c_single})', f'{TWINS.title()}(n={c_twins})']
        ax = plt.gca()
        y_plot_min = int(math.trunc(y_min))
        if y_min - y_plot_min < CLOSE:
            y_plot_min -= 1
        y_plot_max = int(math.ceil(y_max))
        if y_plot_max - y_max < CLOSE:
            y_plot_max += 1
        ax.set_ylim([y_plot_min, y_plot_max])
        set_axis_style(axes, labels)
        axes.set_xlabel('Scenario')
        DEBUG and plt.show()
        fig.savefig(f'violinplot-{target}.svg', format='svg')
        fig.savefig(f'violinplot-{target}.png', format='png')
        plt.close()

        n_sg, n_tw = 1, 1
        t_sg, d_sg, t_tw, d_tw = [], [], [], []
        tx, ty, sc = [], [], []
        for lab, dur in zip(x, y):
            if lab == SINGLE:
                tx.append(n_sg)
                ty.append(dur)
                sc.append(SINGLE)
                t_sg.append(n_sg)
                d_sg.append(dur)
                n_sg += 3
            elif lab == TWINS:
                tx.append(n_tw)
                ty.append(dur)
                sc.append(TWINS)
                t_tw.append(n_tw)
                d_tw.append(dur)
                n_tw += 1.5
        del fig
        del axes
        mpl.rcParams['lines.linewidth'] = 0.7

        frame = pd.DataFrame({'x': tx, 'y': ty, 'scenario': sc})
        final_plot = sns.lmplot(
            x='x',
            y='y',
            hue='scenario',
            data=frame,
            robust=True,
            ci=95,
            markers=['v', '^'],
            palette=dict(single='b', twins='r'),
            scatter_kws={'s': 5},
        )
        fig = final_plot.fig
        axes = plt.gca()
        axes.set_ylim([y_plot_min, y_plot_max])
        axes.set_xlim([0, None])
        axes.yaxis.grid(True)
        axes.xaxis.grid(True)
        axes.set_ylabel('')
        axes.set_xlabel(f'Rank in: [{early}, {late}]')

        fig.savefig(f'timeseries-{target}.svg', format='svg')
        fig.savefig(f'timeseries-{target}.png', format='png')
        DEBUG and plt.show()
        plt.close()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
