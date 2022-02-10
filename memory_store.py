class MemoryStorage:

    def __init__(self):
        self.data = {}

    def set(self, key: str, value: str):
        self.data[key] = value

    def get(self, key) -> str:
        return self.data.get(key, "")
