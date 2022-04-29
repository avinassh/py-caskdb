import os.path
import time
from typing import Optional

from format import KeyEntry, encode_kv, decode_kv, HEADER_SIZE, decode_header

# https://docs.python.org/3.7/tutorial/inputoutput.html#methods-of-file-objects
DEFAULT_WHENCE = 0


class DiskStorage:

    def __init__(self, file_name: str = "data.db"):
        self.file_name = file_name
        self.write_position = 0
        self.key_dir: dict[str, KeyEntry] = {}
        # if the file exists already, then we will load the key_dir
        if os.path.exists(file_name):
            self._init_key_dir()
        self.file = open(file_name, 'a+b')

    def set(self, key: str, value: str):
        timestamp = int(time.time())
        sz, data = encode_kv(timestamp=timestamp, key=key, value=value)
        self._write(data)
        kv = KeyEntry(timestamp=timestamp, position=self.write_position, total_size=sz)
        self.key_dir[key] = kv
        # update last write
        self.write_position += sz

    def get(self, key) -> str:
        kv: Optional[KeyEntry] = self.key_dir.get(key)
        if not kv:
            return ""
        self.file.seek(kv.position, DEFAULT_WHENCE)
        data = self.file.read(kv.total_size)
        _, _, value = decode_kv(data)
        return value

    def _write(self, data: bytes):
        self.file.write(data)
        os.fsync(self.file)

    # we will initialise the key_dir by reading the file
    def _init_key_dir(self):
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

    def close(self):
        os.fsync(self.file)
        self.file.close()
