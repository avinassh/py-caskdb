import unittest

from memory_store import MemoryStorage
from disk_store import DiskStorage


class TestCDBBase():

    def test_get(self, store):
        store.set("name", "jojo")
        self.assertEqual(store.get("name"), "jojo")
        store.close()

    def test_invalid_key(self, store):
        self.assertEqual(store.get("some key"), "")
        store.close()


class TestInMemoryCDB(unittest.TestCase, TestCDBBase):

    def test_get(self):
        store = MemoryStorage()
        super().test_get(store)

    def test_invalid_key(self):
        store = MemoryStorage()
        super().test_invalid_key(store)


class TestDiskCDB(unittest.TestCase, TestCDBBase):

    def test_get(self):
        store = DiskStorage()
        super().test_get(store)

    def test_invalid_key(self):
        store = DiskStorage()
        super().test_invalid_key(store)


if __name__ == '__main__':
    unittest.main()
