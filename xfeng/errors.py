"""XFeng 错误类型（doc.md 第 39 节「错误分类」）。"""


class XFengError(Exception):
    """所有 XFeng 错误（语言语义错误 + 解释器调试限制）的基类。"""

    kind = "XFengError"

    def __init__(self, message: str, line: int | None = None):
        super().__init__(message)
        self.message = message
        self.line = line

    def __str__(self) -> str:
        if self.line is not None:
            return f"{self.kind}: 第 {self.line} 行: {self.message}"
        return f"{self.kind}: {self.message}"


class InvalidProgram(XFengError):
    """语法错误（doc §39.1）：源文件无法形成合法 XFeng 程序。"""

    kind = "InvalidProgram"


class UndefinedFunction(XFengError):
    """未定义函数（doc §39.2）：地图出现函数名字符但没有对应声明。"""

    kind = "UndefinedFunction"


class BoundaryError(XFengError):
    """运行时越界（doc §39.3）：Agent 试图移动到地图之外。"""

    kind = "BoundaryError"


class MaxTicksExceeded(XFengError):
    """解释器调试上限（max_ticks）被触发。

    注意：这**不属于** XFeng 语言语义（doc §31 明确 max_ticks 不是语义的一部分），
    它只是解释器提供的调试限制。
    """

    kind = "MaxTicksExceeded"
