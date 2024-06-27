import unittest

from caskdb import MemoryStorage


class TestInMemoryCaskDB(unittest.TestCase):
    def test_get(self) -> None:
        store = MemoryStorage()
        store.set("name", "jojo")
        self.assertEqual(store.get("name"), "jojo")

    def test_invalid_key(self) -> None:
        store = MemoryStorage()
        self.assertEqual(store.get("some key"), "")

    def test_close(self) -> None:
        store = MemoryStorage()
        store.close()
