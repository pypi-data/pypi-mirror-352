from .color import Color
import sys
import re
from typing import Any, Dict, List, Union, Iterable

__all__ = ['zprint']


class KeyAlignmentSystem:
    """精确的键值对齐系统 - 完全重新设计"""

    def __init__(self):
        # 层级最大长度缓存 {level: max_key_length}
        self.level_cache = {}
        self.raw_keys = {}

    def record_key(self, key: Any, level: int):
        """记录键的原始长度（不带颜色）"""
        raw_key = self._strip_color(str(key))
        self.raw_keys[(level, key)] = len(raw_key)
        return raw_key

    def get_key_length(self, key: Any, level: int) -> int:
        """获取键的原始长度（不带颜色）"""
        return self.raw_keys.get((level, key), len(self._strip_color(str(key))))

    def update_level_max(self, keys: Iterable[Any], level: int):
        """更新层级最大键长度"""
        if level not in self.level_cache:
            self.level_cache[level] = 0

        max_len = max(self.get_key_length(key, level) for key in keys)
        if max_len > self.level_cache[level]:
            self.level_cache[level] = max_len

    def get_padding(self, key: Any, level: int) -> int:
        """获取指定键所需的填充空格数"""
        if level not in self.level_cache:
            return 0

        key_length = self.get_key_length(key, level)
        return self.level_cache[level] - key_length

    @staticmethod
    def _strip_color(text: str) -> str:
        """移除颜色代码"""
        return re.sub(r'\033\[[0-9;]*m', '', str(text))


class PrinterDesign:
    """精心设计的打印主题系统"""
    KEY_COLORS = [
        lambda s: Color(s).bold().blue(),
        lambda s: Color(s).bold().green(),
        lambda s: Color(s).bold().magenta(),
        lambda s: Color(s).bold().yellow(),
    ]

    @staticmethod
    def value_color(s):
        return Color(s).bright_yellow()

    # 列表前缀符号
    LIST_PREFIXES = [
        '-',
        '·',
        '-',
        '·',
    ]

    INDENT_SIZE = 2
    SEPARATOR = ' : '
    MAX_DEPTH = 20
    SHOW_EMPTY = True

    @staticmethod
    def colorize_key(key: Any, level: int) -> str:
        """为键着色，带层级感知"""
        color_idx = min(level, len(PrinterDesign.KEY_COLORS) - 1)
        return PrinterDesign.KEY_COLORS[color_idx](str(key))

    @staticmethod
    def colorize_value(value: Any) -> str:
        """为值着色"""
        return PrinterDesign.value_color(str(value))

    @staticmethod
    def get_list_prefix(level: int) -> str:
        """获取列表前缀符号"""
        prefix_idx = min(level, len(PrinterDesign.LIST_PREFIXES) - 1)
        return PrinterDesign.LIST_PREFIXES[prefix_idx]

    @staticmethod
    def format_empty() -> str:
        """格式化空集合显示"""
        return Color("∅").cyan()

    @staticmethod
    def format_ellipsis() -> str:
        """格式化省略号显示"""
        return Color("…").cyan()


class PrinterCore:

    def __init__(self, alignment: KeyAlignmentSystem):
        self.alignment = alignment
        self.output_lines = []
        self.current_depth = 0

    def flush(self):
        """刷新输出缓冲区"""
        if self.output_lines:
            sys.stdout.write("\n".join(self.output_lines) + "\n")
            sys.stdout.flush()
            self.output_lines = []

    def add_line(self, text: str):
        """添加一行输出"""
        self.output_lines.append(text)
        if len(self.output_lines) >= 100:  # 批量处理
            self.flush()

    def indent_str(self, level: int) -> str:
        """生成缩进字符串"""
        return ' ' * (level * PrinterDesign.INDENT_SIZE)

    def print_dict(self, dct: Dict, level: int):
        """打印字典结构 - 精确对齐每个层级的键"""
        if not dct:
            if PrinterDesign.SHOW_EMPTY:
                self.add_line(
                    f"{self.indent_str(level)}{PrinterDesign.format_empty()}")
            return

        # 安全深度检查
        if self.current_depth >= PrinterDesign.MAX_DEPTH:
            self.add_line(
                f"{self.indent_str(level)}{PrinterDesign.format_ellipsis()}")
            return

        # 更新当前层级最大键长度
        self.alignment.update_level_max(dct.keys(), level)

        # 计算当前层级所有键的最大长度
        max_len = self.alignment.level_cache.get(level, 0)

        for key, value in dct.items():
            # 处理键显示
            colored_key = PrinterDesign.colorize_key(key, level)
            key_length = self.alignment.get_key_length(key, level)
            padding = ' ' * (max_len - key_length)

            # 创建键显示行
            key_line = f"{self.indent_str(level)}{colored_key}{padding}{PrinterDesign.SEPARATOR}"

            # 处理不同类型的值
            if isinstance(value, dict):
                self.add_line(f"{key_line}{PrinterDesign.format_ellipsis()}")
                self.current_depth += 1
                self.print_dict(value, level + 1)
                self.current_depth -= 1
            elif isinstance(value, list):
                self.add_line(f"{key_line}{PrinterDesign.format_ellipsis()}")
                self.current_depth += 1
                self.print_list(value, level + 1)
                self.current_depth -= 1
            else:
                colored_value = PrinterDesign.colorize_value(value)
                self.add_line(f"{key_line}{colored_value}")

    def print_list(self, lst: List, level: int):
        """打印列表结构"""
        if not lst:
            if PrinterDesign.SHOW_EMPTY:
                self.add_line(
                    f"{self.indent_str(level)}{PrinterDesign.format_empty()}")
            return

        # 安全深度检查
        if self.current_depth >= PrinterDesign.MAX_DEPTH:
            self.add_line(
                f"{self.indent_str(level)}{PrinterDesign.format_ellipsis()}")
            return

        prefix = PrinterDesign.get_list_prefix(level)
        indent = self.indent_str(level)

        # 处理列表项
        for item in lst:
            if isinstance(item, dict):
                # 处理列表中的字典项
                for dict_key in item.keys():
                    self.alignment.record_key(dict_key, level + 1)

                self.add_line(
                    f"{indent}{prefix} {PrinterDesign.format_ellipsis()}")
                self.current_depth += 1
                self.print_dict(item, level + 1)
                self.current_depth -= 1
            elif isinstance(item, list):
                self.add_line(
                    f"{indent}{prefix} {PrinterDesign.format_ellipsis()}")
                self.current_depth += 1
                self.print_list(item, level + 1)
                self.current_depth -= 1
            else:
                colored_item = PrinterDesign.colorize_value(item)
                self.add_line(f"{indent}{prefix} {colored_item}")


def zprint(
    content: Union[Dict, List, Any],
    *,
    indent: int = None,
    separator: str = None,
    max_depth: int = None
) -> None:
    """
    精确对齐的美化打印

    :param content: 要打印的内容
    :param indent: 每级缩进空格数
    :param separator: 键值分隔符
    :param max_depth: 最大嵌套深度
    """
    # 应用自定义配置
    original_indent = PrinterDesign.INDENT_SIZE
    original_separator = PrinterDesign.SEPARATOR
    original_max_depth = PrinterDesign.MAX_DEPTH

    try:
        if indent is not None:
            PrinterDesign.INDENT_SIZE = indent
        if separator is not None:
            PrinterDesign.SEPARATOR = separator
        if max_depth is not None:
            PrinterDesign.MAX_DEPTH = max_depth

        alignment_sys = KeyAlignmentSystem()
        printer = PrinterCore(alignment_sys)

        # 根据类型分发打印任务
        if isinstance(content, dict):
            # 预先记录顶层键
            for key in content.keys():
                alignment_sys.record_key(key, 0)

            printer.print_dict(content, 0)
        elif isinstance(content, list):
            printer.print_list(content, 0)
        else:
            printer.add_line(PrinterDesign.colorize_value(str(content)))
    finally:
        # 恢复原始配置
        PrinterDesign.INDENT_SIZE = original_indent
        PrinterDesign.SEPARATOR = original_separator
        PrinterDesign.MAX_DEPTH = original_max_depth

        printer.flush()
