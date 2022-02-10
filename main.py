from memory_store import MemoryStorage
from disk_store import DiskStorage


def memory_db():
    store = MemoryStorage()
    print(store.get("name"))
    store.set("name", "jojo")
    print(store.get("name"), "jojo")


def store_db():
    store = DiskStorage()
    # on the first run, this will print empty string, but on the next run
    # it should print the value from the disk
    print(store.get("name"))
    store.set("name", "haha")
    print(store.get("name"))


if __name__ == '__main__':
    memory_db()
    store_db()
