import os.path
import time
from typing import Optional

from format import KeyEntry, encode_kv, decode_kv

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
        else:
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

    # we will initialise the
    def _init_key_dir(self):
        pass

    def close(self):
        os.fsync(self.file)
        self.file.close()
