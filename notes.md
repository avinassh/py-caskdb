## Auto annotate types

1. install pyannotate and pytest
	
		pip install pyannotate pytest

2. Add the following as `conftest.py` [source](https://github.com/dropbox/pyannotate/blob/a01510d/example/example_conftest.py)

```python
# Configuration for pytest to automatically collect types.
# Thanks to Guilherme Salgado.

import pytest


def pytest_collection_finish(session):
    """Handle the pytest collection finish hook: configure pyannotate.
    Explicitly delay importing `collect_types` until all tests have
    been collected.  This gives gevent a chance to monkey patch the
    world before importing pyannotate.
    """
    from pyannotate_runtime import collect_types
    collect_types.init_types_collection()


@pytest.fixture(autouse=True)
def collect_types_fixture():
    from pyannotate_runtime import collect_types
    collect_types.start()
    yield
    collect_types.stop()


def pytest_sessionfinish(session, exitstatus):
    from pyannotate_runtime import collect_types
    collect_types.dump_stats("type_info.json")
```

3. run pytest and it will automatically generate the type info:
	
        pytest

4. the type info would be generated in `type_info.json`. Use this to write to the files:

	    pyannotate -w --type-info type_info.json disk_store.py example.py format.py memory_store.py tests/test_disk_store.py tests/test_format.py tests/test_memory_store.py