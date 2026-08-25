"""XFeng 源文件解析与合法性校验。

对应 doc.md 第 2–6、20、39.1–39.2 节。
"""

from .errors import InvalidProgram, UndefinedFunction

#: XFeng 1.0 保留地图字符（doc §4）
RESERVED_CHARS = set("SE.()[]<>^?!")

#: 合法地图字符（doc §4）：保留字符 + ASCII 空格
LEGAL_MAP_CHARS = RESERVED_CHARS | {" "}

#: 函数名禁止字符（doc §5.1/5.3/5.4）
FORBIDDEN_NAME_CHARS = RESERVED_CHARS | {"@", "#"}


def is_valid_function_name_char(ch: str) -> bool:
    """一个字符是否满足函数名前 4 条规则（doc §5.1–§5.4）。

    注意：一个函数名还必须「有对应的 @声明」（第 5 条规则），
    那属于调用点校验，不在这里判断。
    """
    if len(ch) != 1:
        return False
    if ch in FORBIDDEN_NAME_CHARS:
        return False
    if ch.isspace():
        return False
    return True


class Map:
    """一张函数地图（doc §3）。"""

    def __init__(self, name: str, rows):
        self.name = name
        self.rows = rows            # list[str]，每一行等长（不做任何 strip/补齐）
        self.height = len(rows)
        self.width = len(rows[0]) if rows else 0
        self.spawn = None           # (x, y) —— S 的位置
        self.exit = None            # (x, y) —— E 的位置

    def cell(self, x: int, y: int) -> str:
        return self.rows[y][x]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def __repr__(self):
        return f"Map(@{self.name} {self.width}×{self.height})"


class Program:
    """解析后的 XFeng 程序。"""

    def __init__(self):
        self.functions = {}   # name -> Map
        self.order = []       # [(name, Map)] 按声明顺序
        self.main = None      # 主程序 Map（@main）


def parse_source(text: str) -> Program:
    """把 XFeng 源文本解析为 Program。

    任何不符合规范之处抛出 InvalidProgram / UndefinedFunction。
    """
    if text.startswith("\ufeff"):
        text = text[1:]  # 去掉 UTF-8 BOM（doc §2.5 按 Unicode code point 处理）

    declarations = []   # [(name, [rows...])]
    current = None
    seen = set()

    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.startswith("#"):
            continue  # 注释行（doc §2.3）：整行忽略，不进地图
        if line.startswith("@"):
            # 声明行（doc §2.2）：必须以行首 @ 开始，且行末不得有其他字符
            name = line[1:]
            _check_declaration(name, lineno)
            if name in seen:
                raise InvalidProgram(f"重复的声明：@{name}", lineno)
            seen.add(name)
            current = [name, []]
            declarations.append(current)
        else:
            # 地图正文行（含空行；空行是长度 0 的地图行，doc §2.4）
            if current is None:
                raise InvalidProgram("地图内容出现在任何声明之前", lineno)
            current[1].append(line)

    program = Program()
    for name, rows in declarations:
        mp = _build_map(name, rows, seen)
        program.order.append((name, mp))
        program.functions[name] = mp
        if name == "main":
            program.main = mp

    if program.main is None:
        raise InvalidProgram("缺少 @main 声明（doc §39.1）")
    return program


def _check_declaration(name: str, lineno: int) -> None:
    if name == "main":
        return  # 主程序声明固定为 @main（doc §2.1）
    if not is_valid_function_name_char(name):
        raise InvalidProgram(
            f"非法声明：@{name}（函数名必须是单个字符，"
            "且不能是保留字符 / 空白 / @ / #）",
            lineno,
        )


def _build_map(name: str, rows, declared: set) -> Map:
    if not rows:
        raise InvalidProgram(f"地图为空：@{name}（每个程序段至少有一行地图）")
    width = len(rows[0])
    if width == 0:
        raise InvalidProgram(f"地图宽度为 0：@{name}（空行不是合法的地图行，doc §2.4）")
    for r in rows:
        if len(r) != width:
            raise InvalidProgram(
                f"地图非矩形：@{name}（各行长度不一致；"
                "解释器不得自动补齐/截断/strip，doc §3.1/§40）"
            )

    s_count = e_count = 0
    spawn = exit_pos = None
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch not in LEGAL_MAP_CHARS:
                if ch in declared:
                    pass  # 函数调用点（doc §21）
                elif is_valid_function_name_char(ch):
                    # doc §39.2：合法函数名字符但没有声明
                    raise UndefinedFunction(
                        f"地图 @{name} 的 ({x},{y}) 出现未声明的函数名 {ch!r}"
                    )
                else:
                    # doc §39.1：非法字符
                    raise InvalidProgram(
                        f"地图 @{name} 的 ({x},{y}) 出现非法字符 {ch!r}"
                    )
            if ch == "S":
                s_count += 1
                spawn = (x, y)
            elif ch == "E":
                e_count += 1
                exit_pos = (x, y)

    if s_count != 1:
        raise InvalidProgram(f"@{name} 必须有且仅有一个 S（实际 {s_count} 个）")
    if e_count != 1:
        raise InvalidProgram(f"@{name} 必须有且仅有一个 E（实际 {e_count} 个）")

    mp = Map(name, rows)
    mp.spawn = spawn
    mp.exit = exit_pos
    return mp
