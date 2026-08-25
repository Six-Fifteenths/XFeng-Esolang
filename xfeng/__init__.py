"""XFeng 1.0 — 二维空间控制流 esolang 解释器核心包。

对应仓库根目录 doc.md 的《XFeng 编程语言规范》。
"""

from .errors import (
    XFengError,
    InvalidProgram,
    UndefinedFunction,
    BoundaryError,
    MaxTicksExceeded,
)
from .parser import (
    parse_source,
    Program,
    Map,
    RESERVED_CHARS,
    LEGAL_MAP_CHARS,
    is_valid_function_name_char,
)
from .interpreter import State, step, run, dir_name

__version__ = "1.0.0"

__all__ = [
    "XFengError",
    "InvalidProgram",
    "UndefinedFunction",
    "BoundaryError",
    "MaxTicksExceeded",
    "parse_source",
    "Program",
    "Map",
    "RESERVED_CHARS",
    "LEGAL_MAP_CHARS",
    "is_valid_function_name_char",
    "State",
    "step",
    "run",
    "dir_name",
]
