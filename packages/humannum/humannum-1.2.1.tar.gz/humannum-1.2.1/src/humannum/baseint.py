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
"""Base Integer."""


class BaseInt(int):
    """Base Integer."""

    @classmethod
    def _cast(cls, value):
        if value is not NotImplemented:
            value = cls(value)
        return value

    @classmethod
    def _casttuple(cls, value):
        if value is not NotImplemented:
            value = tuple(cls(item) for item in value)
        return value

    def __add__(self, other):
        return self._cast(int.__add__(self, other))

    def __sub__(self, other):
        return self._cast(int.__sub__(self, other))

    def __mul__(self, other):
        return self._cast(int.__mul__(self, other))

    def __truediv__(self, other):
        return self._cast(int.__truediv__(self, other))

    def __floordiv__(self, other):
        return self._cast(int.__floordiv__(self, other))

    def __mod__(self, other):
        return self._cast(int.__mod__(self, other))

    def __divmod__(self, other):
        return self._casttuple(int.__divmod__(self, other))

    def __lshift__(self, other):
        return self._cast(int.__lshift__(self, other))

    def __rshift__(self, other):
        return self._cast(int.__rshift__(self, other))

    def __pow__(self, other):
        return self._cast(int.__pow__(self, other))

    def __and__(self, other):
        return self._cast(int.__and__(self, other))

    def __xor__(self, other):
        return self._cast(int.__xor__(self, other))

    def __or__(self, other):
        return self._cast(int.__or__(self, other))

    def __neg__(self):
        return self._cast(int.__neg__(self))

    def __pos__(self):
        return self._cast(int.__pos__(self))

    def __abs__(self):
        return self._cast(int.__abs__(self))

    def __invert__(self):
        return self._cast(int.__invert__(self))

    def __repr__(self):
        return f"{self.__class__.__name__}('{self!s}')"
