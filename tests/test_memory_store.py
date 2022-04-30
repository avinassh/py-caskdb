import unittest

from memory_store import MemoryStorage


class TestInMemoryCDB(unittest.TestCase):
    def test_get(self) -> None:
        store = MemoryStorage()
        store.set("name", "jojo")
        self.assertEqual(store.get("name"), "jojo")

    def test_invalid_key(self) -> None:
        store = MemoryStorage()
        self.assertEqual(store.get("some key"), "")

    def test_close(self) -> None:
        store = MemoryStorage()
        self.assertIsNone(store.close())
        return