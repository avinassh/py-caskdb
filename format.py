import struct
import time

# Our KV on disks looks like this
#
#   timestamp(4 bytes) | key_size (4 bytes) | value_size (4 bytes) | key | value
#
# check https://docs.python.org/3/library/struct.html for this info
# `<` - lil endian
# `L` - long unsigned int
HEADER_FORMAT = "<LLL"
HEADER_SIZE = 12


class KeyEntry:
    def __init__(self, timestamp: int, position: int, total_size: int):
        self.timestamp = timestamp
        self.position = position
        self.total_size = total_size


# for the current key value pair, this method returns the disk encoded bytes along with the size
def encode_kv(timestamp: int, key: str, value: str) -> tuple[int, bytes]:
    header = struct.pack(HEADER_FORMAT, timestamp, len(key), len(value))
    data = b"".join([str.encode(key), str.encode(value)])
    return HEADER_SIZE + len(data), header + data


def decode_header(data: bytes) -> tuple[int, int, int]:
    timestamp, key_size, value_size = struct.unpack(HEADER_FORMAT, data)
    return timestamp, key_size, value_size


def decode_kv(data: bytes) -> tuple[int, str, str]:
    timestamp, key_size, value_size = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
    key_bytes = data[HEADER_SIZE:HEADER_SIZE + key_size]
    value_bytes = data[HEADER_SIZE + key_size:]
    key = key_bytes.decode("utf-8")
    value = value_bytes.decode("utf-8")
    return timestamp, key, value
