class DiskStorage:

    def __init__(self):
        raise NotImplementedError

    def set(self, key: str, value: str):
        raise NotImplementedError

    def get(self, key) -> str:
        raise NotImplementedError
