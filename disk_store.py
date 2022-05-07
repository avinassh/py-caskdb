"""
disk_store module implements DiskStorage class which implements the KV store on the
disk

DiskStorage provides two simple operations to get and set key value pairs. Both key
and value need to be of string type, and all the data is persisted to disk.
During startup, DiskStorage loads all the existing KV pair metadata, and it will
throw an error if the file is invalid or corrupt.

Note that if the database file is large, the initialisation will take time
accordingly. The initialisation is also a blocking operation; till it is completed,
we cannot use the database.

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

from format import KeyEntry, encode_kv, decode_kv, HEADER_SIZE, decode_header

# We use `file.seek` method to move our cursor to certain byte offset for read
# or write operations. The method takes two parameters file.seek(offset, whence).
# The offset says the byte offset and whence says the direction:
#
# whence 0 - beginning of the file
# whence 1 - current cursor position
# whence 2 - end of the file
#
# read more about it here:
# https://docs.python.org/3.7/tutorial/inputoutput.html#methods-of-file-objects
DEFAULT_WHENCE: typing.Final[int] = 0


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


class DiskStorage:
    """
    Implements the KV store on the disk

    Args:
        file_name (str): name of the file where all the data will be written. Just
            passing the file name will save the data in the current directory. You may
            pass the full file location too.

    Attributes:
        file_name (str): name of the file where all the data will be written. Just
            passing the file name will save the data in the current directory. You may
            pass the full file location too.
        file (typing.BinaryIO): file object pointing the file_name
        write_position (int): current cursor position in the file where the data can be
            written
        key_dir (dict[str, KeyEntry]): is a map of key and KeyEntry being the value.
            KeyEntry contains the position of the byte offset in the file where the
            value exists. key_dir map acts as in-memory index to fetch the values
            quickly from the disk
    """

    def __init__(self, file_name: str = "data.db"):
        self.file_name: str = file_name
        self.write_position: int = 0
        self.key_dir: dict[str, KeyEntry] = {}
        # if the file exists already, then we will load the key_dir
        if os.path.exists(file_name):
            self._init_key_dir()
        # we open the file in `a+b` mode:
        # a - says the writes are append only. `a+` means we want append and read
        # b - says that we are operating the file in binary mode (as opposed to the
        #     default string mode)
        self.file: typing.BinaryIO = open(file_name, "a+b")

    def set(self, key: str, value: str) -> None:
        """
        get retrieves the value from the disk and returns. If the key does not exist
        then it returns an empty string

        Args:
            key (str): the key
            value (str): the value
        """
        # The steps to save a KV to disk is simple:
        # 1. Encode the KV into bytes
        # 2. Write the bytes to disk by appending to the file
        # 3. Update KeyDir with the KeyEntry of this key
        timestamp: int = int(time.time())
        sz, data = encode_kv(timestamp=timestamp, key=key, value=value)
        # notice we don't do file seek while writing
        self._write(data)
        kv: KeyEntry = KeyEntry(
            timestamp=timestamp, position=self.write_position, total_size=sz
        )
        self.key_dir[key] = kv
        # update last write position, so that next record can be written from this point
        self.write_position += sz

    def get(self, key: str) -> str:
        """
        get retrieves the value from the disk and returns. If the key does not exist
        then it returns an empty string

        Args:
            key (str): the key

        Returns:
            string
        """
        # How get works?
        # 1. Check if there is any KeyEntry record for the key in KeyDir
        # 2. Return an empty string if key doesn't exist
        # 3. If it exists, then read KeyEntry.total_size bytes starting from the
        #    KeyEntry.position from the disk
        # 4. Decode the bytes into valid KV pair and return the value
        kv: typing.Optional[KeyEntry] = self.key_dir.get(key)
        if not kv:
            return ""
        #  move the current pointer to the right offset
        self.file.seek(kv.position, DEFAULT_WHENCE)
        data: bytes = self.file.read(kv.total_size)
        _, _, value = decode_kv(data)
        return value

    def _write(self, data: bytes) -> None:
        # saving stuff to a file reliably is hard!
        # if you would like to explore and learn more, then
        # start from here: https://danluu.com/file-consistency/
        self.file.write(data)
        # we need to call flush after every write so that our data is moved from
        # runtime buffer to the os buffer
        # read more about here: https://docs.python.org/3/library/os.html#os.fsync
        self.file.flush()
        # calling fsync after every write is important, this assures that our writes
        # are actually persisted to the disk
        os.fsync(self.file.fileno())

    def _init_key_dir(self) -> None:
        # we will initialise the key_dir by reading the contents of the file, record by
        # record. As we read each record, we will also update our KeyDir with the
        # corresponding KeyEntry
        #
        # NOTE: this method is a blocking one, if the DB size is yuge then it will take
        # a lot of time to startup
        print("****----------initialising the database----------****")
        with open(self.file_name, "rb") as f:
            while header_bytes := f.read(HEADER_SIZE):
                timestamp, key_size, value_size = decode_header(data=header_bytes)
                key_bytes = f.read(key_size)
                value_bytes = f.read(value_size)
                key = key_bytes.decode("utf-8")
                value = value_bytes.decode("utf-8")
                total_size = HEADER_SIZE + key_size + value_size
                kv = KeyEntry(
                    timestamp=timestamp,
                    position=self.write_position,
                    total_size=total_size,
                )
                self.key_dir[key] = kv
                self.write_position += total_size
                print(f"loaded k={key}, v={value}")
        print("****----------initialisation complete----------****")

    def close(self) -> None:
        # before we close the file, we need to safely write the contents in the buffers
        # to the disk. Check documentation of DiskStorage._write() to understand
        # following the operations
        self.file.flush()
        os.fsync(self.file.fileno())
        self.file.close()

    def __setitem__(self, key: str, value: str) -> None:
        return self.set(key, value)

    def __getitem__(self, item: str) -> str:
        return self.get(item)
