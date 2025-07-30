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
"""
Human Friendly Numbers.

Numbers created by `bin_()`, `hex()` and `bytesize_()` and
simply stay in their representation even through calculations if they are the left operand.
Any string conversion results in a pretty formatted number.

Binary:

    >>> from humannum import bin_
    >>> bin_(42)
    Bin('0b101010')
    >>> str(bin_(42))
    '0b101010'
    >>> str(bin_(42) + 24)
    '0b1000010'
    >>> str(bin_(42, width=16))
    '0b0000000000101010'

Hexadecimal

    >>> from humannum import hex_
    >>> hex_(42)
    Hex('0x2A')
    >>> str(hex_(42))
    '0x2A'
    >>> str(hex_(42) + 24)
    '0x42'
    >>> str(hex_(42, width=16))
    '0x002A'

Bytes:

    >>> from humannum import bytesize
    >>> bytesize_(42)
    Bytesize('42 bytes')
    >>> str(bytesize_(42))
    '42 bytes'
    >>> str(bytesize_(42) + 24)
    '66 bytes'
    >>> str(bytesize_(42*1000))
    '42000 bytes'
    >>> str(bytesize_(42*1024))
    '42 KB'

Frequency

    >>> from humannum import freq
    >>> freq(42)
    Freq('42Hz')
    >>> str(freq(42))
    '42Hz'
    >>> str(freq(42) + 24)
    '66Hz'
    >>> str(freq(42*1000))
    '42kHz'
"""

from typing import Any

from .binary import Bin
from .bytesize import Bytesize
from .converter import int_
from .freq import Freq
from .hex import Hex


def bin_(value: Any, width: int | None = None) -> Bin:
    """
    Integer with binary representation.

    The binary format is kept through calculations!!!

    Args:
        value: Value

    Keyword Args:
        width: Width in bits.

    ??? example "Usage"

        Basics:

            >>> bin_(32)
            Bin('0b100000')
            >>> str(bin_(32) + 3)
            '0b100011'
            >>> str(bin_(-32))
            '-0b100000'
            >>> str(bin_("0x50"))
            '0b01010000'
            >>> str(bin_("-0b1010000"))
            '-0b1010000'
            >>> str(bin_("0o50"))
            '0b101000'
            >>> bin_("5Z")
            Traceback (most recent call last):
                ...
            ValueError: invalid literal for int() with base 10: '5Z'

        The width in bits is optional:

            >>> bin_(32, width=16)
            Bin('0b0000000000100000')

        The width can be also taken from the value:

            >>> bin_("16'd50")
            Bin('0b0000000000110010')

        Smaller widths are not truncated:

            >>> bin_("16'd50", width=4)
            Bin('0b110010')
    """
    return Bin(value, width=width)


def hex_(value: Any, width: int | None = None) -> Hex:
    """
    Integer with hexadecial representation.

    The hexadecial format is kept through calculations

    Args:
        value: Value

    Keyword Args:
        width: Width in bits.

    ??? example "Usage"

        Basics:

            >>> hex_(32)
            Hex('0x20')
            >>> str(hex_(32) + 3)
            '0x23'
            >>> str(hex_(-32))
            '-0x20'
            >>> str(hex_("0x50"))
            '0x50'
            >>> str(hex_("-0b1010000"))
            '-0x50'
            >>> str(hex_("0o50"))
            '0x28'
            >>> hex_("5Z")
            Traceback (most recent call last):
                ...
            ValueError: invalid literal for int() with base 10: '5Z'

        A width in bits is optional:

            >>> hex_(32, width=16)
            Hex('0x0020')

        If given, the default width is taken from the value:

            >>> hex_("16'd50")
            Hex('0x0032')

        Smaller widths are not truncated:

            >>> hex_("16'd50", width=4)
            Hex('0x32')
    """
    return Hex(value, width=width)


def bytesize_(value: Any) -> Bytesize:
    """
    Integer with hexadecial representation.

    The hexadecial format is kept through calculations

    Args:
        value: Value

    ??? example "Usage"

        >>> bytesize_(32*1024*1024)
        Bytesize('32 MB')
        >>> str(bytesize_(32*1024*1024))
        '32 MB'
        >>> str(bytesize_("45000.2 KB"))
        '46080204 bytes'
        >>> str(bytesize_(Bytesize(40*1024)))
        '40 KB'
        >>> str(bytesize_("0x1000"))
        '4 KB'
        >>> str(int(bytesize_("0x1000")))
        '4096'
        >>> str(bytesize_("-0x1000"))
        '-4096 bytes'
        >>> bytesize_("5FOO")
        Traceback (most recent call last):
            ...
        ValueError: Invalid number of bytes: '5FOO'
    """
    return Bytesize(value)


def freq(value: Any) -> Freq:
    """
    Integer with hexadecial representation.

    The hexadecial format is kept through calculations

    Args:
        value: Value

    ??? example "Usage"

        >>> freq(32*1000*1000)
        Freq('32MHz')
        >>> str(freq(32*1000*1000))
        '32MHz'
        >>> str(freq("45000.2 Mhz"))
        '45000.2MHz'
        >>> str(freq(Freq(40*1000)))
        '40kHz'
        >>> str(freq("0x1000"))
        '4096Hz'
        >>> str(int(freq("0x1000")))
        '4096'
        >>> str(freq("-0x1000"))
        '-4096Hz'
        >>> freq("5FOO")
        Traceback (most recent call last):
            ...
        ValueError: Invalid frequency: '5FOO'
    """
    return Freq(value)


# Obsolete
bytes_ = bytesize_
Bytes = Bytesize

__all__ = [
    "Bin",
    "Bytes",
    "Bytesize",
    "Hex",
    "bin_",
    "bytes_",
    "bytesize_",
    "hex_",
    "int_",
]
