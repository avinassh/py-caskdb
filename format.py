import struct

# Our KV on disks looks like this
#
#   timestamp(4 bytes) | key_size (4 bytes) | value_size (4 bytes) | key | value
#
# The first three fields form the header
#
# check https://docs.python.org/3/library/struct.html for this info
# `<` - lil endian
# `L` - long unsigned int
HEADER_FORMAT = "<LLL"
HEADER_SIZE = 12


class KeyEntry:
    """
    KeyEntry keeps the metadata about the value. KeyEntry also is a value in the
    KeyDir map.

    Args:
        timestamp (int): Timestamp at which we wrote the KV pair to the disk. The value
            is current time in seconds since the epoch.
        position (int): The position is the byte offset in the file where the data
            exists
        total_size(int): Total size of bytes of the value
    """

    def __init__(self, timestamp: int, position: int, total_size: int):
        self.timestamp = timestamp
        self.position = position
        self.total_size = total_size


# Our header looks like the following:
#
# timestamp(4 bytes) | key_size (4 bytes) | value_size (4 bytes)
#
# encode_header encodes these values into bytes.
def encode_header(timestamp: int, key_size: int, value_size: int) -> bytes:
    return struct.pack(HEADER_FORMAT, timestamp, key_size, value_size)


# for the current key value pair, this method returns the disk encoded bytes along
# with the size
def encode_kv(timestamp: int, key: str, value: str) -> tuple[int, bytes]:
    header = encode_header(timestamp, len(key), len(value))
    data = b"".join([str.encode(key), str.encode(value)])
    return HEADER_SIZE + len(data), header + data


def decode_kv(data: bytes) -> tuple[int, str, str]:
    timestamp, key_size, value_size = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
    key_bytes = data[HEADER_SIZE : HEADER_SIZE + key_size]
    value_bytes = data[HEADER_SIZE + key_size :]
    key = key_bytes.decode("utf-8")
    value = value_bytes.decode("utf-8")
    return timestamp, key, value


# decode_header decodes bytes into timestamp, key length and value length.
def decode_header(data: bytes) -> tuple[int, int, int]:
    timestamp, key_size, value_size = struct.unpack(HEADER_FORMAT, data)
    return timestamp, key_size, value_size
