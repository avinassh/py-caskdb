from memory_store import MemoryStorage
from disk_store import DiskStorage


def memory_db() -> None:
    store = MemoryStorage()
    print(store.get("name"))
    store.set("name", "jojo")
    print(store.get("name"), "jojo")


def store_db() -> None:
    store = DiskStorage("data.db")
    # on the first run, this will print empty string, but on the next run
    # it should print the value from the disk
    print(store.get("name"))
    store.set("name", "haha")
    print(store.get("name"))
    store.close()


def store_books() -> None:
    store = DiskStorage("books.db")
    books = {
        "crime and punishment": "dostoevsky",
        "anna karenina": "tolstoy",
        "war and peace": "tolstoy",
        "hamlet": "shakespeare",
        "othello": "shakespeare",
        "brave new world": "huxley",
        "dune": "frank herbert",
    }
    for k, v in books.items():
        store.set(k, v)
        print(f"set k={k}, v={v}")
        print(f"get k={k}, v={store.get(k)}")

    for k in books.keys():
        print(f"get k={k}, v={store.get(k)}")
    store.close()


if __name__ == "__main__":
    # memory_db()
    store_db()
    store_books()
