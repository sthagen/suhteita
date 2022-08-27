"""Provide a simple JSON store for event records."""
import copy
import datetime as dti
import json
import pathlib
from typing import Dict, Union, no_type_check

from suhteita import ENCODING, NODE_INDICATOR, STORE, TS_FORMAT_PAYLOADS, Clocking

TS_FORMAT_STORE = '%Y%m%dT%H%M%S.%fZ'


@no_type_check
class Store:
    @no_type_check
    def __init__(
        self, context: Dict[str, Union[str, dti.datetime]], setup: object, folder_path: Union[pathlib.Path, str] = STORE
    ):
        self.store = pathlib.Path(folder_path)
        self.identity = context['identity']
        self.start_time = context['start_time']
        self.end_ts = None
        self.total_secs = 0.0
        self.node_indicator = NODE_INDICATOR
        self.store.mkdir(parents=True, exist_ok=True)
        self.db_name = f'{self.identity}-{self.start_time.strftime(TS_FORMAT_STORE)}-{self.node_indicator}.json'
        self.rank = 0
        self.db = {
            '_meta': {
                'scenario': context.get('scenario', 'unknown'),
                'identity': self.identity,
                'node_indicator': str(self.node_indicator),
                'target': context.get('target', 'unknown'),
                'mode': context.get('mode', 'unknown'),
                'project': context.get('project', 'unknown'),
                'db_name': self.db_name,
                'db_path': str(self.store / self.db_name),
                'start_ts': self.start_time.strftime(TS_FORMAT_PAYLOADS),
                'total_secs': self.total_secs,
                'end_ts': self.end_ts,
                'has_failures_declared': None,
                'has_failures_detected': None,
                'setup': copy.deepcopy(setup.__dict__),
            },
            'events': [],
        }

    @no_type_check
    def add(self, label: str, ok: bool, clk: Clocking, comment: str = ''):
        self.rank += 1
        self.db['events'].append(
            {
                'rank': self.rank,
                'label': label,
                'ok': ok,
                'start_ts': clk[0],
                'duration_usecs': clk[1],
                'end_ts': clk[2],
                'comment': comment,
            }
        )

    @no_type_check
    def dump(self, end_time: dti.datetime, has_failures: bool = False):
        self.end_time = end_time
        self.db['_meta']['end_ts'] = self.end_time.strftime(TS_FORMAT_PAYLOADS)
        self.db['_meta']['total_secs'] = (self.end_time - self.start_time).total_seconds()
        self.db['_meta']['has_failures_declared'] = has_failures
        detect_failures = False
        for event in self.db['events']:
            if not event['ok']:
                detect_failures = True
        self.db['_meta']['has_failures_detected'] = detect_failures
        with open(self.store / self.db_name, 'wt', encoding=ENCODING) as handle:
            json.dump(self.db, handle)
