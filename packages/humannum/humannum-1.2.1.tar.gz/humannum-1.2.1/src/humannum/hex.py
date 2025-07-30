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
"""Hexadecimal Class."""

from typing import Any

from . import converter
from .baseint import BaseInt


class Hex(BaseInt):
    """
    Integer with hexadecimal representation.

    ??? example "Usage"

            >>> Hex(50)
            Hex('0x32')
            >>> Hex('0x32')
            Hex('0x32')
            >>> str(Hex(50))
            '0x32'
            >>> str(Hex(500))
            '0x1F4'

        This hexadecimal value behaves like a normal integer.

            >>> 8 + Hex(8)
            16
            >>> str(Hex(8) + 8)
            '0x10'
            >>> str(Hex(8) - 2)
            '0x6'
            >>> str(Hex(8) * 3)
            '0x18'
            >>> str(Hex(8) / 3)
            '0x2'
            >>> str(Hex(8) // 3)
            '0x2'
            >>> str(Hex(8) % 5)
            '0x3'
            >>> str(Hex(8) << 1)
            '0x10'
            >>> str(Hex(8) >> 1)
            '0x4'
            >>> str(Hex(8) ** 2)
            '0x40'
            >>> str(Hex(9) & 3)
            '0x1'
            >>> str(Hex(8) | 3)
            '0xB'
            >>> str(Hex(9) ^ 3)
            '0xA'
            >>> divmod(Hex(9), 3)
            (Hex('0x3'), Hex('0x0'))
            >>> str(~Hex(9))
            '-0xA'
            >>> str(-Hex(9))
            '-0x9'
            >>> str(abs(Hex(-9)))
            '0x9'
            >>> str(+Hex(9))
            '0x9'

            >>> Hex(8) | 'A'
            Traceback (most recent call last):
            ...
            TypeError: unsupported operand type(s) for |: 'Hex' and 'str'
            >>> divmod(Hex(9), 'A')
            Traceback (most recent call last):
            ...
            TypeError: unsupported operand type(s) for divmod(): 'Hex' and 'str'

        Corner Cases:

            >>> str(Hex(0))
            '0x0'
            >>> str(Hex(-5))
            '-0x5'

        Width:

            >>> a = Hex(3)
            >>> str(a)
            '0x3'
            >>> a.width=6
            >>> str(a)
            '0x03'

            >>> a = Hex(-3)
            >>> str(a)
            '-0x3'
            >>> a.width=6
            >>> str(a)
            '-0x03'
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
            pat = "0x%%0%dX" % ((width + 3) / 4,)  # noqa: UP031
        else:
            pat = "0x%X"
        if value >= 0:
            return pat % (value,)
        return ("-" + pat) % (-value,)
