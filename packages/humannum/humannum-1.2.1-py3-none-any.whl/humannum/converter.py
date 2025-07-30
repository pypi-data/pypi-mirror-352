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
Converter.
"""

import re
from functools import lru_cache
from math import ceil, log2

_int_prefixes = (
    (re.compile(r"\A(?P<s>-)?(?P<w>)0h(?P<v>.*)"), 16),
    (re.compile(r"\A(?P<s>-)?(?P<w>)0d(?P<v>.*)"), 10),
    (re.compile(r"\A(?P<s>-)?(?P<w>)0x(?P<v>.*)"), 16),
    (re.compile(r"\A(?P<s>-)?(?P<w>)0o(?P<v>.*)"), 8),
    (re.compile(r"\A(?P<s>-)?(?P<w>)0b(?P<v>.*)"), 2),
    (re.compile(r"\A(?P<s>-)?(?P<w>\d+)?'h(?P<v>.*)"), 16),
    (re.compile(r"\A(?P<s>-)?(?P<w>\d+)?'d(?P<v>.*)"), 10),
    (re.compile(r"\A(?P<s>-)?(?P<w>\d+)?'o(?P<v>.*)"), 8),
    (re.compile(r"\A(?P<s>-)?(?P<w>\d+)?'b(?P<v>.*)"), 2),
)


@lru_cache(maxsize=32)
def int_(value, strcast=None) -> tuple[int, int | None]:
    """
    Convert Integer.

    Returns:
        Value, Width

    ??? example "Usage"

            >>> int_('0h10')
            (16, 8)
            >>> int_('0h010')
            (16, 12)
            >>> int_('0d10')
            (10, 7)
            >>> int_('0x10')
            (16, 8)
            >>> int_('0o10')
            (8, 6)
            >>> int_('0b10')
            (2, 2)
            >>> int_("8'h10")
            (16, 8)
            >>> int_("8'd10")
            (10, 8)
            >>> int_("8'o10")
            (8, 8)
            >>> int_("8'b10")
            (2, 8)
    """
    if isinstance(value, str):
        value = value.strip()
        for pat, base in _int_prefixes:
            mat = pat.match(value)
            if mat:
                sign = -1 if mat.group("s") else 1
                value = sign * int(mat.group("v"), base)
                wid = mat.group("w")
                if wid:
                    width = int(wid)
                else:
                    width = ceil(len(mat.group("v")) * log2(base))
                return int(value), width
        if strcast:
            value = strcast(value)
    return int(value), None
