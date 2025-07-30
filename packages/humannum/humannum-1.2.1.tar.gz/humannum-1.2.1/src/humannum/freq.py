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

import numbers
from typing import Any, NamedTuple

from humanfriendly import round_number
from humanfriendly.compat import is_string
from humanfriendly.text import format, tokenize

from . import converter
from .baseint import BaseInt


class _Unit(NamedTuple):
    divider: int
    symbol: str


# Common disk size units in binary (base-2) and decimal (base-10) multiples.
units = (
    _Unit(1000**1, "kHz"),
    _Unit(1000**2, "MHz"),
    _Unit(1000**3, "GHz"),
    _Unit(1000**4, "THz"),
)


class Freq(BaseInt, int):
    """
    Integer Frequency.

    ??? example "Usage"

            >>> Freq(1)
            Freq('1Hz')
            >>> Freq('1 Hz')
            Freq('1Hz')
            >>> Freq('20 mhz')
            Freq('20MHz')
            >>> str(Freq(1))
            '1Hz'
            >>> str(Freq(50))
            '50Hz'
            >>> str(Freq(50 * 1000))
            '50kHz'
            >>> str(Freq(50 * 1000 * 1000))
            '50MHz'
            >>> str(Freq(50 * 1000 * 1000 * 1000))
            '50GHz'
            >>> str(Freq(999))
            '999Hz'
            >>> str(Freq(1000))
            '1kHz'
            >>> str(Freq(1001))
            '1001Hz'

        This value behaves like a normal integer.

            >>> str(Freq(50) + 50)
            '100Hz'
            >>> 50 + Freq(50)
            100
            >>> str(Freq(8) - 2)
            '6Hz'
            >>> str(Freq(8) * 3)
            '24Hz'
            >>> str(Freq(8) / 3)
            '2Hz'
            >>> str(Freq(8) // 3)
            '2Hz'
            >>> str(Freq(8) % 5)
            '3Hz'
            >>> str(Freq(8) << 1)
            '16Hz'
            >>> str(Freq(8) >> 1)
            '4Hz'
            >>> str(Freq(8) ** 2)
            '64Hz'
            >>> str(Freq(9) & 3)
            '1Hz'
            >>> str(Freq(8) | 3)
            '11Hz'
            >>> str(Freq(9) ^ 3)
            '10Hz'
            >>> str(divmod(Freq(9), 3))
            "(Freq('3Hz'), Freq('0Hz'))"
            >>> str(~Freq(9))
            '-10Hz'
            >>> str(-Freq(9))
            '-9Hz'
            >>> str(abs(Freq(-9)))
            '9Hz'
            >>> str(+Freq(9))
            '9Hz'

            >>> Freq(8) | 'A'
            Traceback (most recent call last):
            ...
            TypeError: unsupported operand type(s) for |: 'Freq' and 'str'
            >>> divmod(Freq(9), 'A')
            Traceback (most recent call last):
            ...
            TypeError: unsupported operand type(s) for divmod(): 'Freq' and 'str'

        An integer can retrieved by

            >>> Freq(50) + 50
            Freq('100Hz')
            >>> int(Freq(50) + 50)
            100

        Corner Cases:

            >>> Freq(0)
            Freq('0Hz')
            >>> Freq(-5)
            Freq('-5Hz')
    """

    def __new__(cls, value: Any):
        try:
            value = converter.int_(value, strcast=_parse_freq)[0]
        except Exception:
            raise ValueError(f"Invalid frequency: '{value}'") from None
        return super().__new__(cls, value)

    def __str__(self):
        return _format_freq(int(self))


def _parse_freq(value) -> int:
    tokens = tokenize(value)
    if tokens and isinstance(tokens[0], numbers.Number):
        normalized_unit = tokens[1].lower() if len(tokens) == 2 and is_string(tokens[1]) else ""  # noqa: PLR2004
        if len(tokens) == 1 or normalized_unit == "hz":
            return int(tokens[0])  # type: ignore[call-overload]
        if normalized_unit:
            for unit in units:
                if normalized_unit == unit.symbol.lower():
                    return int(float(tokens[0]) * unit.divider)  # type: ignore[arg-type]
    msg = "Failed to parse frequency! (input %r was tokenized as %r)"
    raise InvalidFreq(format(msg, value, tokens))


def _format_freq(num):
    """
    Format a byte count as a human readable file size.
    """
    for unit in reversed(units):
        divider = unit.divider
        if num >= divider:
            number = round_number(float(num) / divider)
            if float(number) * divider == num:
                return f"{number}{unit.symbol}"
    return f"{num}Hz"


class InvalidFreq(Exception):  # noqa: N818
    """Invalid Frequency."""
