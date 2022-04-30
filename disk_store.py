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
# read more about it here: https://docs.python.org/3.7/tutorial/inputoutput.html#methods-of-file-objects
DEFAULT_WHENCE: int = 0


class DiskStorage:
    """
    Implements the KV store on the disk

    Args:
        file_name (str): name of the file where all the data will be written. Just passing the
            file name will save the data in the current directory. You may pass the
            full file location too.

    Attributes:
        file_name (str): name of the file where all the data will be written. Just passing the
            file name will save the data in the current directory. You may pass the
            full file location too.
        file (typing.TextIO): file object pointing the file_name
        write_position (int): current cursor position in the file where the data can be
            written
        key_dir (dict[str, KeyEntry]): is a map of key and KeyEntry being the value. This
            map acts as in-memory index to fetch the values quickly from the disk
    """

    def __init__(self, file_name: str = "data.db"):
        self.file_name: str = file_name
        self.write_position: int = 0
        self.key_dir: dict[str, KeyEntry] = {}
        # if the file exists already, then we will load the key_dir
        if os.path.exists(file_name):
            self._init_key_dir()
        self.file: typing.BinaryIO = open(file_name, 'a+b')

    def set(self, key: str, value: str) -> None:
        timestamp = int(time.time())
        sz, data = encode_kv(timestamp=timestamp, key=key, value=value)
        self._write(data)
        kv = KeyEntry(timestamp=timestamp, position=self.write_position, total_size=sz)
        self.key_dir[key] = kv
        # update last write position
        self.write_position += sz

    def get(self, key: str) -> str:
        kv: typing.Optional[KeyEntry] = self.key_dir.get(key)
        if not kv:
            return ""
        self.file.seek(kv.position, DEFAULT_WHENCE)
        data = self.file.read(kv.total_size)
        _, _, value = decode_kv(data)
        return value

    def _write(self, data: bytes) -> None:
        self.file.write(data)
        os.fsync(self.file)

    # we will initialise the key_dir by reading the file
    def _init_key_dir(self) -> None:
        print("****----------initialising the database----------****")
        with open(self.file_name, "rb") as f:
            while header_bytes := f.read(HEADER_SIZE):
                timestamp, key_size, value_size = decode_header(data=header_bytes)
                key_bytes = f.read(key_size)
                value_bytes = f.read(value_size)
                key = key_bytes.decode("utf-8")
                value = value_bytes.decode("utf-8")
                total_size = HEADER_SIZE + key_size + value_size
                kv = KeyEntry(timestamp=timestamp, position=self.write_position, total_size=total_size)
                self.key_dir[key] = kv
                self.write_position += total_size
                print(F"loaded k={key}, v={value}")
        print("****----------initialisation complete----------****")

    def close(self) -> None:
        os.fsync(self.file)
        self.file.close()
