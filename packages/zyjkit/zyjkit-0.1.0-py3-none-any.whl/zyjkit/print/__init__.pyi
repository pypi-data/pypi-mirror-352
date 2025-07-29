from typing import Callable
from .color import Color, SupportsStr


bold: Callable[[SupportsStr], Color]
dim: Callable[[SupportsStr], Color]
italic: Callable[[SupportsStr], Color]
underline: Callable[[SupportsStr], Color]
blink: Callable[[SupportsStr], Color]
blink_fast: Callable[[SupportsStr], Color]
reverse: Callable[[SupportsStr], Color]
hidden:  Callable[[SupportsStr], Color]
through: Callable[[SupportsStr], Color]

# fg
black: Callable[[SupportsStr], Color]
red: Callable[[SupportsStr], Color]
green: Callable[[SupportsStr], Color]
yellow: Callable[[SupportsStr], Color]
blue:  Callable[[SupportsStr], Color]
magenta: Callable[[SupportsStr], Color]
cyan: Callable[[SupportsStr], Color]
white: Callable[[SupportsStr], Color]
bright_black: Callable[[SupportsStr], Color]
bright_red: Callable[[SupportsStr], Color]
bright_green: Callable[[SupportsStr], Color]
bright_yellow: Callable[[SupportsStr],
                        Color]
bright_blue: Callable[[SupportsStr], Color]
bright_magenta: Callable[[SupportsStr],
                         Color]
bright_cyan: Callable[[SupportsStr], Color]
bright_white: Callable[[SupportsStr], Color]


# bg

bg_black: Callable[[SupportsStr], Color]
bg_red: Callable[[SupportsStr], Color]
bg_green:  Callable[[SupportsStr], Color]
bg_yellow: Callable[[SupportsStr], Color]
bg_blue: Callable[[SupportsStr], Color]
bg_magenta: Callable[[SupportsStr], Color]
bg_cyan: Callable[[SupportsStr], Color]
bg_white: Callable[[SupportsStr], Color]
bg_bright_black: Callable[[SupportsStr],
                          Color]
bg_bright_red: Callable[[SupportsStr], Color]

bg_bright_green: Callable[[SupportsStr],
                          Color]
bg_bright_yellow: Callable[[SupportsStr],
                           Color]
bg_bright_green: Callable[[SupportsStr],
                          Color]
bg_bright_blue: Callable[[SupportsStr], Color]
bg_bright_magenta: Callable[[SupportsStr],
                            Color]
bg_bright_cyan: Callable[[SupportsStr], Color]
bg_bright_white: Callable[[SupportsStr],
                          Color]
