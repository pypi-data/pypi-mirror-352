from typing import Any, Dict, Final, Union, List, Literal


CODES_STYLE: Final = {
    "bold": 1,
    "dim": 2,
    "italic": 3,
    "underline": 4,
    "blink": 5,
    "blink_fast": 6,
    "reverse": 7,
    "hidden": 8,
    "through": 9,
}

CODES_FG: Final = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "bright_black": 90,
    "bright_red": 91,
    "bright_green": 92,
    "bright_yellow": 93,
    "bright_blue": 94,
    "bright_magenta": 95,
    "bright_cyan": 96,
    "bright_white": 97,
}

CODES_BG: Final = {
    "bg_black": 40,
    "bg_red": 41,
    "bg_green": 42,
    "bg_yellow": 43,
    "bg_blue": 44,
    "bg_magenta": 45,
    "bg_cyan": 46,
    "bg_white": 47,
    "bg_bright_black": 100,
    "bg_bright_red": 101,
    "bg_bright_green": 102,
    "bg_bright_yellow": 103,
    "bg_bright_blue": 104,
    "bg_bright_magenta": 105,
    "bg_bright_cyan": 106,
    "bg_bright_white": 107,
}

CODES = {**CODES_STYLE, **CODES_FG, **CODES_BG, }

# 从最高位开始
BIT_STYLE: Final[Dict[int, int]] = {
    0x100: 9,  # 第一个插入的最高位
    0x080: 8,
    0x040: 7,
    0x020: 6,
    0x010: 5,
    0x008: 4,
    0x004: 3,
    0x002: 2,
    0x001: 1,
}

StyleName = Literal[
    'bold', 'dim', 'italic', 'underline',
    'blink', 'blink_fast', 'reverse', 'hidden', 'through'
]

FgColorName = Literal[
    'black', 'red', 'green', 'yellow', 'blue',
    'magenta', 'cyan', 'white', 'bright_black',
    'bright_red', 'bright_green', 'bright_yellow',
    'bright_blue', 'bright_magenta', 'bright_cyan', 'bright_white'
]

ColorName = FgColorName
CodeName = Union[StyleName, ColorName]

STYLE_MASK = 0x1FF
FG_MASK = 0x0000FE00  # 7 位前景色 (bits 9-15)
BG_MASK = 0x00FF0000  # 8 位背景色 (bits 16-23)


class Code:
    """ANSI 终端颜色和样式控制类，使用位运算高效管理状态。

    该类通过单个 32 位整数存储状态，结构如下：
    | unused(8) | bg(8) | fg(7) | styles(9) |

    示例用法：
        >>> c = Code()
        >>> c.set_fg('red')
        >>> c.add_style('bold')

    注意：
    - 背景色设置使用前景色名称，内部自动转换
    """

    __slots__ = ('_state', '_text')

    def __init__(self, text: Any = '', state: int = 0):
        # 存储结构: | unused(8) | bg(8) | fg(7) | styles(9) |
        self._state = state
        self._text = text

    def __bool__(self) -> bool:
        return len(self._text) > 0

    def __len__(self) -> int:
        return len(self._text)

    @property
    def style_code(self) -> int:
        return self._state & STYLE_MASK

    @property
    def fg_code(self) -> int:
        return self._state & FG_MASK

    @property
    def bg_code(self) -> int:
        return self._state & BG_MASK

    def copy(self) -> 'Code':
        return self.__class__(self._text, self._state)

    def has_style(self, name: StyleName) -> bool:
        """检查样式"""
        return bool(self._state & (1 << (CODES_STYLE[name] - 1)))

    def add_style(self, name: StyleName) -> 'Code':
        """添加样式"""
        self._state |= (1 << (CODES_STYLE[name] - 1))
        return self

    def remove_style(self, name: StyleName) -> 'Code':
        """移除样式"""
        self._state &= ~(1 << (CODES_STYLE[name] - 1))
        return self

    def set_fg(self, name: ColorName) -> 'Code':
        """设置前景色 - 移动到 bits 9-15"""
        self._state = (self._state & ~FG_MASK) | (
            (CODES_FG[name] & 0x7F) << 9)
        return self

    def remove_fg(self) -> 'Code':
        """移除前景色"""
        self._state &= ~FG_MASK
        return self

    def set_bg(self, name: ColorName) -> 'Code':
        """设置背景色 - 移动到 bits 16-23"""
        bg_code = CODES_FG[name] + 10  # 前景修正为背景
        self._state = (self._state & ~BG_MASK) | ((bg_code & 0xFF) << 16)
        return self

    def remove_bg(self) -> 'Code':
        """移除背景色"""
        self._state &= ~BG_MASK
        return self

    def clear(self) -> 'Code':
        """重置所有状态"""
        self._state = 0
        return self

    def ansi_codes(self) -> List[int]:
        """获取当前状态对应的原始 ANSI 代码列表"""

        codes = []
        state = self._state

        # 样式
        bit = state & STYLE_MASK
        while bit:
            m1 = bit - 1
            h = bit & ~m1 if (bit & m1) else bit
            codes.append(BIT_STYLE[h])
            bit ^= h

        # 前景色 (bits 9-15)
        if fg_code := (state & FG_MASK) >> 9:
            codes.append(fg_code)

        # 背景色 (bits 16-23)
        if bg_code := (state & BG_MASK) >> 16:
            codes.append(bg_code)

        return codes

    @property
    def ansi_start(self) -> str:
        return f"\033[{';'.join(map(str, self.ansi_codes()))}m"

    @property
    def ansi_reset(self) -> str:
        return "\033[0m"

    def wrap(self, text: Any = None) -> str:
        """封装"""
        if text:
            self._text = text

        text_str = str(self._text)

        if not text_str or not self._state:
            return text_str
        return f"{self.ansi_start}{text_str}{self.ansi_reset}"

    def __str__(self):
        return self.wrap()
