import unittest

from memory_store import MemoryStorage
from disk_store import DiskStorage


class TestCaskDB(unittest.TestCase):

    def test_get(self):
        store = DiskStorage()
        store.set("name", "jojo")
        self.assertEqual(store.get("name"), "jojo")
        self.assertEqual(store.get("some key"), "")
        store.close()

    def test_invalid_key(self):
        store = DiskStorage()
        self.assertEqual(store.get("some key"), "")
        store.close()


if __name__ == '__main__':
    unittest.main()
