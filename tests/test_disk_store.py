import os
import tempfile
import typing
import unittest

from disk_store import DiskStorage


class TempStorageFile:
    def __init__(self, path: typing.Optional[str] = None):
        if path:
            self.path = path
            return

        fd, self.path = tempfile.mkstemp()
        os.close(fd)

    def clean_up(self):
        os.remove(self.path)


class TestDiskCDB(unittest.TestCase):
    def test_get(self):
        t = TempStorageFile()
        store = DiskStorage(file_name=t.path)
        store.set("name", "jojo")
        self.assertEqual(store.get("name"), "jojo")
        store.close()
        t.clean_up()

    def test_get_new_file(self):
        t = TempStorageFile(path="temp.db")
        store = DiskStorage(file_name=t.path)
        store.set("name", "jojo")
        self.assertEqual(store.get("name"), "jojo")
        store.close()

        # check for key again
        store = DiskStorage(file_name=t.path)
        self.assertEqual(store.get("name"), "jojo")
        store.close()
        t.clean_up()

    def test_invalid_key(self):
        t = TempStorageFile()
        store = DiskStorage(file_name=t.path)
        self.assertEqual(store.get("some key"), "")
        store.close()
        t.clean_up()

    def test_persistence(self):
        t = TempStorageFile()
        store = DiskStorage(file_name=t.path)

        tests = {
            "crime and punishment": "dostoevsky",
            "anna karenina": "tolstoy",
            "war and peace": "tolstoy",
            "hamlet": "shakespeare",
            "othello": "shakespeare",
            "brave new world": "huxley",
            "dune": "frank herbert",
        }
        for k, v in tests.items():
            store.set(k, v)
            self.assertEqual(store.get(k), v)
        store.close()

        store = DiskStorage(file_name=t.path)
        for k, v in tests.items():
            self.assertEqual(store.get(k), v)
        store.close()
        t.clean_up()
