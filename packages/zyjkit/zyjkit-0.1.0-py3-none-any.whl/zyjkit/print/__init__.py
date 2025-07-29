from .code import CODES_FG, CODES_STYLE, ColorName, StyleName
from .color import Color
from .zprint import zprint  # noqa: F401


def _create_style_func(code_name: StyleName):
    return lambda text: Color(text).add_style(code_name)


def _create_fg_func(code_name: ColorName):
    return lambda text: Color(text).set_fg(code_name)


def _create_bg_func(code_name: ColorName):
    return lambda text: Color(text).set_bg(code_name)


# style
for style in CODES_STYLE:
    globals()[style] = _create_style_func(style)

# color
for color in CODES_FG:
    globals()[color] = _create_fg_func(color)
    globals()[f"bg_{color}"] = _create_bg_func(color)
