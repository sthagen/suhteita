import datetime as dti

from suhteita.store import Store


def test_store_class():
    context = {
        'target': 'target',
        'mode': 'mode',
        'project': 'project',
        'scenario': 'scenario',
        'identity': 'identity',
        'start_time': dti.datetime.now(tz=dti.timezone.utc),
    }

    class Setup:
        pass

    store = Store(context=context, setup=Setup(), folder_path='/tmp/away')
    assert store.db
    tx = dti.datetime.now(tz=dti.timezone.utc)
    store.add('x', True, (str(tx), 42.0, str(tx)), 'yes')
    store.dump(tx, has_failures=True)
