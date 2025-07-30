#
# MIT License
#
# Copyright (c) 2023-2025 nbiotcloud
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""Bytes."""

from typing import Any

from humanfriendly import disk_size_units, parse_size, round_number
from humanfriendly.text import pluralize

from . import converter
from .baseint import BaseInt


class Bytesize(BaseInt, int):
    """
    Integer with byte size representation.

    ??? example "Usage"

            >>> Bytesize(1)
            Bytesize('1 byte')
            >>> Bytesize('1 byte')
            Bytesize('1 byte')
            >>> str(Bytesize(1))
            '1 byte'
            >>> str(Bytesize(50))
            '50 bytes'
            >>> str(Bytesize(50 * 1024))
            '50 KB'
            >>> str(Bytesize(1023))
            '1023 bytes'
            >>> str(Bytesize(1024))
            '1 KB'
            >>> str(Bytesize(1025))
            '1025 bytes'

        This value behaves like a normal integer.

            >>> str(Bytesize(50) + 50)
            '100 bytes'
            >>> 50 + Bytesize(50)
            100
            >>> str(Bytesize(8) - 2)
            '6 bytes'
            >>> str(Bytesize(8) * 3)
            '24 bytes'
            >>> str(Bytesize(8) / 3)
            '2 bytes'
            >>> str(Bytesize(8) // 3)
            '2 bytes'
            >>> str(Bytesize(8) % 5)
            '3 bytes'
            >>> str(Bytesize(8) << 1)
            '16 bytes'
            >>> str(Bytesize(8) >> 1)
            '4 bytes'
            >>> str(Bytesize(8) ** 2)
            '64 bytes'
            >>> str(Bytesize(9) & 3)
            '1 byte'
            >>> str(Bytesize(8) | 3)
            '11 bytes'
            >>> str(Bytesize(9) ^ 3)
            '10 bytes'
            >>> str(divmod(Bytesize(9), 3))
            "(Bytesize('3 bytes'), Bytesize('0 bytes'))"
            >>> str(~Bytesize(9))
            '-10 bytes'
            >>> str(-Bytesize(9))
            '-9 bytes'
            >>> str(abs(Bytesize(-9)))
            '9 bytes'
            >>> str(+Bytesize(9))
            '9 bytes'

            >>> Bytesize(8) | 'A'
            Traceback (most recent call last):
            ...
            TypeError: unsupported operand type(s) for |: 'Bytesize' and 'str'
            >>> divmod(Bytesize(9), 'A')
            Traceback (most recent call last):
            ...
            TypeError: unsupported operand type(s) for divmod(): 'Bytesize' and 'str'

        An integer can retrieved by

            >>> Bytesize(50) + 50
            Bytesize('100 bytes')
            >>> int(Bytesize(50) + 50)
            100

        Corner Cases:

            >>> Bytesize(0)
            Bytesize('0 bytes')
            >>> Bytesize(-5)
            Bytesize('-5 bytes')
    """

    def __new__(cls, value: Any):
        try:
            value = converter.int_(value, strcast=_parse_bytes)[0]
        except Exception:
            raise ValueError(f"Invalid number of bytes: '{value}'") from None
        return super().__new__(cls, value)

    def __str__(self):
        ret = _format_size(int(self))
        return ret.replace("iB", "B")


def _parse_bytes(value):
    return parse_size(value, binary=True)


def _format_size(num_bytes):
    """
    Format a byte count as a human readable file size.
    """
    for unit in reversed(disk_size_units):
        if num_bytes >= unit.binary.divider:
            number = round_number(float(num_bytes) / unit.binary.divider)
            if float(number) * unit.binary.divider == num_bytes:
                return pluralize(number, unit.binary.symbol, unit.binary.symbol)
    return pluralize(num_bytes, "byte")
