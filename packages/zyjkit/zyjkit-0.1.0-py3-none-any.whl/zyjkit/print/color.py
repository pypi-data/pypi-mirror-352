from collections import deque
import re
from .code import CODES_FG, CODES_STYLE, Code, ColorName, StyleName
from typing import Any, List, Protocol, Union, runtime_checkable


@runtime_checkable
class SupportsStr(Protocol):
    def __str__(self) -> str: ...


_Text = SupportsStr


class Frags:
    __slots__ = ('_frags', '_code')

    def __init__(self, frags: List[Union['Frags', Code, _Text]] = None, code: Code = None):
        self._frags = deque(frags) if frags else deque()
        self._code = code if code else Code()

    def append(self, frag: _Text):
        if bool(frag):
            self._frags.append(frag)

    def copy(self):
        return self.__class__([frag.copy() if isinstance(frag, Code) else frag for frag in self._frags])

    def __len__(self):
        return sum(len(frag) for frag in self._frags)

    def __bool__(self):
        return len(self) > 0

    def __str__(self):
        return self._code.wrap(''.join(str(frag) for frag in self._frags))

    def add_style(self, name: StyleName):
        self._code.add_style(name)

    def set_fg(self, name: ColorName):
        self._code.set_fg(name)

    def set_bg(self, name: ColorName):
        self._code.set_bg(name)


class Color:
    # _value 的值只能为 Frags 或 Code
    __slots__ = ('_value', '_cache_str')

    def __init__(self, value: 'Color' | List[Union['Color', _Text]] | _Text):
        if isinstance(value, list):
            self._value = Frags([frag._value.copy() if isinstance(
                frag, Color) else frag for frag in value])
        else:
            self._value = value._value.copy() if isinstance(
                value, Color) else Code(value)

        self._cache_str = None

    def __call__(self) -> 'Color':
        return self

    def __getattr__(self, name: str) -> 'Color':
        if name in CODES_STYLE:
            return self.add_style(name)
        elif name in CODES_FG:
            return self.set_fg(name)
        elif name.startswith('bg_'):
            return self.set_bg(name[3:])
        else:
            raise AttributeError(f'Color 没有属性 {name}')

    def __len__(self):
        return len(self._value)

    def __str__(self):
        if not self._cache_str:
            self._cache_str = str(self._value)
        return self._cache_str

    def __bool__(self):
        return bool(self._value)

    def __add__(self, other: Any) -> 'Color':
        return self.__class__([self, str(other)])

    def __radd__(self, other: Any) -> 'Color':
        return self.__class__([str(other), self])

    def clear_cache(self):
        self._cache_str = None

    def is_frags(self) -> bool:
        return isinstance(self._value, Frags)

    def is_frag(self) -> bool:
        return isinstance(self._value, Code)

    def add_style(self, name: StyleName) -> 'Color':
        self._value.add_style(name)
        self.clear_cache()
        return self

    def set_fg(self, name: ColorName) -> 'Color':
        self._value.set_fg(name)
        self.clear_cache()
        return self

    def set_bg(self, name: ColorName) -> 'Color':
        self._value.set_bg(name)
        self.clear_cache()
        return self

    def __format__(self, format_spec: str):

        # 无 format_spec
        if not format_spec:
            return super().__format__(format_spec)

        ns = re.findall(r'\d+', format_spec)

        # 无效 format_spec
        if not ns:
            return super().__format__(format_spec)

        text = str(self)
        exc_size = len(text) - len(self)

        # 无样式的情况
        if exc_size <= 0:
            return super().__format__(format_spec)

        _spec = format_spec.replace(
            ns[0],
            f'{int(ns[0]) + exc_size}'
        )
        return f'{text:{_spec}}'
