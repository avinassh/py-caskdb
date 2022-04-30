import unittest

from memory_store import MemoryStorage


class TestInMemoryCDB(unittest.TestCase):
    def test_get(self):
        store = MemoryStorage()
        store.set("name", "jojo")
        self.assertEqual(store.get("name"), "jojo")

    def test_invalid_key(self):
        store = MemoryStorage()
        self.assertEqual(store.get("some key"), "")

    def test_close(self):
        store = MemoryStorage()
        self.assertIsNone(store.close())
