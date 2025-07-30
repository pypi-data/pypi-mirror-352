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
"""Binary Class."""

from typing import Any

from . import converter
from .baseint import BaseInt


class Bin(BaseInt):
    """
    Integer with binary representation.

    ??? example "Usage"

            >>> Bin(50)
            Bin('0b110010')
            >>> Bin('0b110010')
            Bin('0b110010')
            >>> str(Bin(50))
            '0b110010'
            >>> str(Bin(500))
            '0b111110100'

        This binary value behaves like a normal integer, but the first value dominates.

            >>> 8 + Bin(8)
            16
            >>> str(Bin(8) + 8)
            '0b10000'
            >>> str(Bin(8) - 2)
            '0b110'
            >>> str(Bin(8) * 3)
            '0b11000'
            >>> str(Bin(8) / 3)
            '0b10'
            >>> str(Bin(8) // 3)
            '0b10'
            >>> str(Bin(8) % 5)
            '0b11'
            >>> str(Bin(8) << 1)
            '0b10000'
            >>> str(Bin(8) >> 1)
            '0b100'
            >>> str(Bin(8) ** 2)
            '0b1000000'
            >>> str(Bin(9) & 3)
            '0b1'
            >>> str(Bin(8) | 3)
            '0b1011'
            >>> str(Bin(9) ^ 3)
            '0b1010'
            >>> divmod(Bin(9), 3)
            (Bin('0b11'), Bin('0b0'))
            >>> str(~Bin(9))
            '-0b1010'
            >>> str(-Bin(9))
            '-0b1001'
            >>> str(abs(Bin(-9)))
            '0b1001'
            >>> str(+Bin(9))
            '0b1001'
            >>> Bin(8) | 'A'
            Traceback (most recent call last):
            ...
            TypeError: unsupported operand type(s) for |: 'Bin' and 'str'
            >>> divmod(Bin(9), 'A')
            Traceback (most recent call last):
            ...
            TypeError: unsupported operand type(s) for divmod(): 'Bin' and 'str'

        Corner Cases:

            >>> str(Bin(0))
            '0b0'
            >>> str(Bin(-5))
            '-0b101'

        Width:

            >>> a = Bin(3)
            >>> str(a)
            '0b11'
            >>> a.width=6
            >>> str(a)
            '0b000011'

            >>> a = Bin(-3)
            >>> str(a)
            '-0b11'
            >>> a.width=6
            >>> str(a)
            '-0b000011'
    """

    def __new__(cls, value: Any, width: int | None = None):
        value = converter.int_(value)[0]
        return super().__new__(cls, value)

    def __init__(self, value: Any, width: int | None = None):
        if width is not None:
            self.width = width
        else:
            self.width = converter.int_(value)[1]  # type: ignore[assignment]

    def __str__(self):
        value = int(self)
        width = self.width
        if width:
            if value >= 0:
                return "0b" + bin(value)[2:].zfill(width)
            return "-0b" + bin(-value)[2:].zfill(width)
        return bin(value)
