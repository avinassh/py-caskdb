import random
import struct
import time
import typing
import unittest
import uuid

from format import encode_header, decode_header, encode_kv, decode_kv, HEADER_SIZE
from format import KeyEntry


def get_random_header() -> tuple[int, int, int]:
    # we use 4 bytes to store the int, so max value cannot be greater than
    # the following
    max_size: int = (2**32) - 1
    random_int: typing.Callable[[], int] = lambda: random.randint(0, max_size)
    return random_int(), random_int(), random_int()


def get_random_kv() -> tuple[int, str, str, int]:
    return (
        int(time.time()),
        str(uuid.uuid4()),
        str(uuid.uuid4()),
        HEADER_SIZE + (2 * len(str(uuid.uuid4()))),
    )


class Header(typing.NamedTuple):
    timestamp: int
    key_size: int
    val_size: int


class KeyValue(typing.NamedTuple):
    timestamp: int
    key: str
    val: str
    sz: int


class TestHeaderOp(unittest.TestCase):
    def header_test(self, tt: Header) -> None:
        data = encode_header(tt.timestamp, tt.key_size, tt.val_size)
        t, k, v = decode_header(data)
        self.assertEqual(tt.timestamp, t)
        self.assertEqual(tt.key_size, k)
        self.assertEqual(tt.val_size, v)

    def test_header_serialisation(self) -> None:
        tests: typing.List[Header] = [
            Header(10, 10, 10),
            Header(0, 0, 0),
            Header(10000, 10000, 10000),
        ]
        for tt in tests:
            self.header_test(tt)

    def test_random(self) -> None:
        for _ in range(100):
            tt = Header(*get_random_header())
            self.header_test(tt)

    def test_bad(self) -> None:
        # trying to encode an int with size more than 4 bytes should raise an error
        self.assertRaises(struct.error, encode_header, 2**32, 5, 5)


class TestEncodeKV(unittest.TestCase):
    def kv_test(self, tt: KeyValue) -> None:
        sz, data = encode_kv(tt.timestamp, tt.key, tt.val)
        t, k, v = decode_kv(data)
        self.assertEqual(tt.timestamp, t)
        self.assertEqual(tt.key, k)
        self.assertEqual(tt.val, v)
        self.assertEqual(tt.sz, sz)

    def test_KV_serialisation(self) -> None:
        tests: typing.List[KeyValue] = [
            KeyValue(10, "hello", "world", HEADER_SIZE + 10),
            KeyValue(0, "", "", HEADER_SIZE),
        ]
        for tt in tests:
            self.kv_test(tt)

    def test_random(self) -> None:
        for _ in range(100):
            tt = KeyValue(*get_random_kv())
            self.kv_test(tt)


class TestKeyEntry(unittest.TestCase):
    # dumb test to increase the coverage
    def test_init(self) -> None:
        ke = KeyEntry(10, 10, 10)
        self.assertEqual(ke.timestamp, 10)
        self.assertEqual(ke.position, 10)
        self.assertEqual(ke.total_size, 10)
