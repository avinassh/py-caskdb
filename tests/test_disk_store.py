import os
import tempfile
import typing
import unittest

from disk_store import DiskStorage


class TempStorageFile:
    """
    TempStorageFile provides a wrapper over the temporary files which are used in
    testing.

    Python has two APIs to create temporary files, tempfile.TemporaryFile and
    tempfile.mkstemp. Files created by tempfile.TemporaryFile gets deleted as soon as
    they are closed. Since we need to do tests for persistence, we might open and
    close a file multiple times. Files created using tempfile.mkstemp don't have this
    limitation, but they have to deleted manually. They don't get deleted when the file
    descriptor is out scope or our program has exited.

    Args:
        path (str): path to the file where our data needs to be stored. If the path
            parameter is empty, then a temporary will be created using tempfile API
    """

    def __init__(self, path: typing.Optional[str] = None):
        if path:
            self.path = path
            return

        fd, self.path = tempfile.mkstemp()
        os.close(fd)

    def clean_up(self) -> None:
        # NOTE: you might be tempted to use the destructor method `__del__`, however
        # destructor method gets called whenever the object goes out of scope, and it
        # will delete our database file. Having a separate method would give us better
        # control.
        os.remove(self.path)


class TestDiskCaskDB(unittest.TestCase):
    def setUp(self) -> None:
        self.file: TempStorageFile = TempStorageFile()

    def tearDown(self) -> None:
        self.file.clean_up()

    def test_get(self) -> None:
        store = DiskStorage(file_name=self.file.path)
        store.set("name", "jojo")
        self.assertEqual(store.get("name"), "jojo")
        store.close()

    def test_invalid_key(self) -> None:
        store = DiskStorage(file_name=self.file.path)
        self.assertEqual(store.get("some key"), "")
        store.close()

    def test_dict_api(self) -> None:
        store = DiskStorage(file_name=self.file.path)
        store["name"] = "jojo"
        self.assertEqual(store["name"], "jojo")
        store.close()

    def test_persistence(self) -> None:
        store = DiskStorage(file_name=self.file.path)

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

        store = DiskStorage(file_name=self.file.path)
        for k, v in tests.items():
            self.assertEqual(store.get(k), v)
        store.close()

    def test_deletion(self) -> None:
        store = DiskStorage(file_name=self.file.path)

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
        for k, _ in tests.items():
            store.set(k, "")
        store.set("end", "yes")
        store.close()

        store = DiskStorage(file_name=self.file.path)
        for k, v in tests.items():
            self.assertEqual(store.get(k), "")
        self.assertEqual(store.get("end"), "yes")
        store.close()


class TestDiskCaskDBExistingFile(unittest.TestCase):
    def test_get_new_file(self) -> None:
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
