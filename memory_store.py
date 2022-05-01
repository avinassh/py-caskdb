class MemoryStorage:
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        self.data[key] = value

    def get(self, key: str) -> str:
        return self.data.get(key, "")

    def close(self) -> bool:
        # NOTE: ideally, I would want this to have () -> None signature, but for some
        # reason mypy complains about this:
        #
        # tests/test_memory_store.py:19: error: "close" of "MemoryStorage" does not
        #   return a value
        #
        # check here for more: https://github.com/python/mypy/issues/6549
        return True
