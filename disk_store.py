"""
disk_store module implements DiskStorage class which implements the KV store on the
disk

DiskStorage provides two simple operations to get and set key value pairs. Both key and
value needs to be of string type. All the data is persisted to disk. During startup,
DiskStorage loads all the existing KV pair metadata.  It will throw an error if the
file is invalid or corrupt.

Do note that if the database file is large, then the initialisation will take time
accordingly. The initialisation is also a blocking operation, till it is completed
the DB cannot be used.

Typical usage example:

    disk: DiskStorage = DiskStore(file_name="books.db")
    disk.set(key="othello", value="shakespeare")
    author: str = disk.get("othello")
    # it also supports dictionary style API too:
    disk["hamlet"] = "shakespeare"
"""
import os.path
import time
import typing
from dataclasses import dataclass

from format import encode_kv, decode_kv, decode_header, HEADER_SIZE


# DiskStorage is a Log-Structured Hash Table as described in the BitCask paper. We
# keep appending the data to a file, like a log. DiskStorage maintains an in-memory
# hash table called KeyDir, which keeps the row's location on the disk.
#
# The idea is simple yet brilliant:
#   - Write the record to the disk
#   - Update the internal hash table to point to that byte offset
#   - Whenever we get a read request, check the internal hash table for the address,
#       fetch that and return
#
# KeyDir does not store values, only their locations.
#
# The above approach solves a lot of problems:
#   - Writes are insanely fast since you are just appending to the file
#   - Reads are insanely fast since you do only one disk seek. In B-Tree backed
#       storage, there could be 2-3 disk seeks
#
# However, there are drawbacks too:
#   - We need to maintain an in-memory hash table KeyDir. A database with a large
#       number of keys would require more RAM
#   - Since we need to build the KeyDir at initialisation, it will affect the startup
#       time too
#   - Deleted keys need to be purged from the file to reduce the file size
#
# Read the paper for more details: https://riak.com/assets/bitcask-intro.pdf


@dataclass
class Value:
    position: int
    timestamp: int
    size: int


class DiskStorage:
    """
    Implements the KV store on the disk

    Args:
        file_name (str): name of the file where all the data will be written. Just
            passing the file name will save the data in the current directory. You may
            pass the full file location too.
    """

    disk_file: typing.BinaryIO
    append_position: int = 0
    key_dir: dict[str, Value] = {}

    def __init__(self, file_name: str = "data.db"):
        """
        1. check if file exists. if not, create the file
        2. initialize in memory storage from file
        :param file_name:
        """
        if os.path.exists(file_name):
            self._make_key_dir(file_name)
        self.disk_file = open(file_name, "ab+")

    def set(self, key: str, value: str) -> None:
        timestamp = int(time.time())
        size, row_to_write = encode_kv(timestamp, key, value)

        val = Value(position=self.append_position, timestamp=timestamp, size=size)

        self.disk_file.write(row_to_write)
        self.disk_file.flush()
        self.append_position = self.append_position + size
        self.key_dir[key] = val

    def get(self, key: str) -> str:
        val = self.key_dir.get(key, None)
        if not val:
            return ""
        self.disk_file.seek(val.position)
        bytes_to_decode = self.disk_file.read(val.size)
        _, _, value = decode_kv(bytes_to_decode)

        self.disk_file.seek(self.append_position)

        return value

    def close(self) -> None:
        self.disk_file.flush()
        self.disk_file.close()

    def __setitem__(self, key: str, value: str) -> None:
        return self.set(key, value)

    def __getitem__(self, item: str) -> str:
        return self.get(item)

    def _make_key_dir(self, file_name: str) -> None:
        print(f"populating key_dir from {file_name}")
        with open(file_name, "rb") as f:
            while header := f.read(HEADER_SIZE):
                timestamp, key_size, value_size = decode_header(header)
                row_size = HEADER_SIZE + key_size + value_size
                val = Value(
                    timestamp=timestamp, position=self.append_position, size=row_size
                )
                self.append_position = self.append_position + row_size
                key = f.read(key_size).decode("utf-8")

                # skip value_size to ignore actual value data
                _ = f.read(value_size)
                print(f"storing {key} in key_dir")
                self.key_dir[key] = val
