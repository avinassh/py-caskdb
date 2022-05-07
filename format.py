"""
format module provides encode/decode functions for serialisation and deserialisation
operations

format module is generic and does not have any disk or memory specific code.

The disk storage deals with bytes; you cannot just store a string or object without
converting it to bytes. The programming languages provide abstractions where you
don't have to think about all this when storing things in memory (i.e. RAM).
Consider the following example where you are storing stuff in a hash table:

    books = {}
    books["hamlet"] = "shakespeare"
    books["anna karenina"] = "tolstoy"

In the above, the language deals with all the complexities:

    - allocating space on the RAM so that it can store data of `books`
    - whenever you add data to `books`, convert that to bytes and keep it in the memory
    - whenever the size of `books` increases, move that to somewhere in the RAM so that
      we can add new items

Unfortunately, when it comes to disks, we have to do all this by ourselves, write
code which can allocate space, convert objects to/from bytes and many other operations.

format module provides two functions which help us with serialisation of data.

    encode_kv - takes the key value pair and encodes them into bytes
    decode_kv - takes a bunch of bytes and decodes them into key value pairs

**workshop note**

For the workshop, the functions will have the following signature:

    def encode_kv(timestamp: int, key: str, value: str) -> tuple[int, bytes]
    def decode_kv(data: bytes) -> tuple[int, str, str]
"""

import struct
import typing

# Our key value pair, when stored on disk looks like this:
#   ┌───────────┬──────────┬────────────┬─────┬───────┐
#   │ timestamp │ key_size │ value_size │ key │ value │
#   └───────────┴──────────┴────────────┴─────┴───────┘
#
# This is analogous to a typical database's row (or a record). The total length of
# the row is variable, depending on the contents of the key and value.
#
# The first three fields form the header:
#   ┌───────────────┬──────────────┬────────────────┐
#   │ timestamp(4B) │ key_size(4B) │ value_size(4B) │
#   └───────────────┴──────────────┴────────────────┘
#
# These three fields store unsigned integers of size 4 bytes, giving our header a
# fixed length of 12 bytes. Timestamp field stores the time the record we
# inserted in unix epoch seconds. Key size and value size fields store the length of
# bytes occupied by the key and value. The maximum integer
# stored by 4 bytes is 4,294,967,295 (2 ** 32 - 1), roughly ~4.2GB. So, the size of
# each key or value cannot exceed this. Theoretically, a single row can be as large
# as ~8.4GB.
#
# We use `struct.pack` method to serialise our header to bytes. `struct.pack` function
# looks like this:
#
#   struct.pack(format, v1, v2, ...) -> bytes
#
# The first argument is a format string, which specifies how the parameters v1, v2, ...
# should be encoded. `HEADER_FORMAT` is our format string for the header.
# Check the struct documentation https://docs.python.org/3/library/struct.html
# to understand how to construct such a string.
#
# `<` - lil endian to be used to encode the integer
# `L` - represents long unsigned int (4 bytes). We have three fields, hence `LLL`
HEADER_FORMAT: typing.Final[str] = "<LLL"
HEADER_SIZE: typing.Final[int] = 12


class KeyEntry:
    """
    KeyEntry keeps the metadata about the KV, specially the position of
    the byte offset in the file. Whenever we insert/update a key, we create a new
    KeyEntry object and insert that into KeyDir.

    Args:
        timestamp (int): Timestamp at which we wrote the KV pair to the disk. The value
            is current time in seconds since the epoch.
        position (int): The position is the byte offset in the file where the data
            exists
        total_size(int): Total size of bytes of the value. We use this value to know
            how many bytes we need to read from the file
    """

    def __init__(self, timestamp: int, position: int, total_size: int):
        self.timestamp: int = timestamp
        self.position: int = position
        self.total_size: int = total_size


def encode_header(timestamp: int, key_size: int, value_size: int) -> bytes:
    """
    encode_header encodes the data into bytes using the `HEADER_FORMAT` format
    string

    Args:
        timestamp (int): Timestamp at which we wrote the KV pair to the disk. The value
            is current time in seconds since the epoch.
        key_size (int): size of the key (cannot exceed the maximum)
        value_size (int): size of the value (cannot exceed the maximum)

    Returns:
        byte object containing the encoded data

    Raises:
        struct.error when parameters don't match the specific type / size
    """
    return struct.pack(HEADER_FORMAT, timestamp, key_size, value_size)


def encode_kv(timestamp: int, key: str, value: str) -> tuple[int, bytes]:
    """
    encode_kv encodes the KV pair into bytes

    Args:
        timestamp (int): Timestamp at which we wrote the KV pair to the disk. The value
            is current time in seconds since the epoch.
        key (str): the key (cannot exceed the maximum size)
        value (str): the value (cannot exceed the maximum size)

    Returns:
        tuple containing the size of encoded bytes and the byte object

    Raises:
        struct.error when parameters don't match the specific type / size
    """
    header: bytes = encode_header(timestamp, len(key), len(value))
    data: bytes = b"".join([str.encode(key), str.encode(value)])
    return HEADER_SIZE + len(data), header + data


def decode_kv(data: bytes) -> tuple[int, str, str]:
    """
    decode_kv decodes the data bytes into appropriate KV pair

    Args:
        data (bytes): byte object containing the encoded KV data

    Returns:
        A tuple containing:

            timestamp (int): timestamp in epoch seconds
            key (str): the key
            value (str): the value

    Raises:
        struct.error: when parameters don't match the specific type / size
        IndexError: if the length of bytes is shorter than expected
        UnicodeDecodeError: if the key or values bytes could not be decoded to string
    """
    timestamp, key_size, value_size = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
    key_bytes: bytes = data[HEADER_SIZE : HEADER_SIZE + key_size]
    value_bytes: bytes = data[HEADER_SIZE + key_size :]
    key: str = key_bytes.decode("utf-8")
    value: str = value_bytes.decode("utf-8")
    return timestamp, key, value


def decode_header(data: bytes) -> tuple[int, int, int]:
    """
    decode_header decodes the bytes into header using the `HEADER_FORMAT` format
    string

    Args:
        data (bytes): byte object containing the encoded header data

    Returns:
        A tuple containing:

            timestamp (int): timestamp in epoch seconds
            key_size (int): size of the key
            value_size (int): size of the value

    Raises:
        struct.error: when parameters don't match the specific type / size
    """
    timestamp, key_size, value_size = struct.unpack(HEADER_FORMAT, data)
    return timestamp, key_size, value_size
