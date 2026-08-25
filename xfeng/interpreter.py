"""XFeng 执行引擎。

严格遵循 doc.md：
  - 核心顺序：确定方向 → 移动一格 → 执行到达格（§11/§33）
  - 函数调用/返回的调用栈语义（§29/§36/§37）
  - 越界 → BoundaryError（§39.3）
  - max_ticks 仅为调试限制，不属于语言语义（§31）
"""

from .errors import XFengError, BoundaryError, MaxTicksExceeded
from .parser import Program

DIR_NAMES = {(1, 0): "右", (-1, 0): "左", (0, 1): "下", (0, -1): "上"}


def dir_name(d) -> str:
    return DIR_NAMES.get(tuple(d), "?")


class State:
    """运行时状态 Σ = (P, x, y, h, L, R, C)（doc §32）。"""

    __slots__ = ("P", "x", "y", "h", "L", "R", "stack", "ticks")

    def __init__(self, program: Program, L_in: int = 0, R_in: int = 0):
        self.P = program.main
        self.x, self.y = program.main.spawn
        self.h = 1          # 初始 h = +1（doc §10）
        self.L = L_in
        self.R = R_in
        self.stack = []     # [(Map, x, y)] 调用栈帧（doc §29：只保存调用者地图与调用点）
        self.ticks = 0


def step(state: State, program: Program) -> dict:
    """单步执行：返回事件描述并修改 state。

    事件 dict 字段：
      tick, map, x, y, cell, L, R, h, depth   —— 该 tick 开始时的状态快照
      action: 'move' | 'call' | 'return' | 'halt'
      dir / to / arrived / callee / result 等按 action 附加。
    """
    P = state.P
    c = P.cell(state.x, state.y)
    ev = {
        "tick": state.ticks,
        "map": P.name,
        "x": state.x,
        "y": state.y,
        "cell": c,
        "L": state.L,
        "R": state.R,
        "h": state.h,
        "depth": len(state.stack),
    }

    if c == "E":
        # doc §8：主程序 E → 终止；函数 E → 返回
        if P is program.main:
            ev["action"] = "halt"
            ev["result"] = state.L
            state.ticks += 1
            return ev
        if not state.stack:
            raise XFengError("内部错误：函数 E 但调用栈为空")
        pm, (px, py) = state.stack.pop()
        state.P, state.x, state.y = pm, px, py
        ev["action"] = "return"
        ev["to_map"] = pm.name
        ev["to"] = (px, py)
        ev["call_point"] = (px, py)
        state.ticks += 1
        return ev

    # 第一步：确定运动方向（doc §11.1 / §34）
    if c == " ":
        dx, dy = 0, 1          # 自由落体
    elif c == "^":
        dx, dy = 0, -1         # 梯子
    elif c == "?":
        dx, dy = (0, 1) if state.L == 0 else (state.h, 0)   # 左门
    elif c == "!":
        dx, dy = (0, 1) if state.R == 0 else (state.h, 0)   # 右门
    else:
        dx, dy = state.h, 0    # 水平地面：. S ( [ ) ] < > 函数名

    ev["dir"] = (dx, dy)

    # 第二步：移动（doc §11.2）
    nx, ny = state.x + dx, state.y + dy
    if not P.in_bounds(nx, ny):
        raise BoundaryError(
            f"@{P.name} ({state.x},{state.y}) 处字符 {c!r} 向{dir_name((dx, dy))}"
            f"移动到 ({nx},{ny})，超出地图边界"
        )
    state.x, state.y = nx, ny
    ev["to"] = (nx, ny)

    # 第三步：执行到达格（doc §11.3 / §35）
    c2 = P.cell(nx, ny)
    ev["arrived"] = c2
    ev["action"] = "move"  # 默认动作；下面按字符覆盖
    if c2 == "E":
        # doc §8/§35：到达主程序 E → 当场 HALT；到达函数 E → 当场 RETURN
        if P is program.main:
            ev["action"] = "halt"
            ev["result"] = state.L
        else:
            if not state.stack:
                raise XFengError("内部错误：函数 E 但调用栈为空")
            pm, (px, py) = state.stack.pop()
            state.P, state.x, state.y = pm, px, py
            ev["action"] = "return"
            ev["to_map"] = pm.name
            ev["call_point"] = (px, py)
    elif c2 == "(":
        state.L += 1
    elif c2 == "[":
        state.L -= 1
    elif c2 == ")":
        state.R += 1
    elif c2 == "]":
        state.R -= 1
    elif c2 == "<":
        state.h = -1
    elif c2 == ">":
        state.h = 1
    elif c2 in program.functions:
        # 函数调用（doc §36）：压入调用点，转移到 S_F，保留 L/R/h
        state.stack.append((P, (nx, ny)))
        state.P = program.functions[c2]
        state.x, state.y = state.P.spawn
        ev["action"] = "call"
        ev["callee"] = c2
        ev["callee_map"] = state.P.name
        ev["callee_spawn"] = (state.x, state.y)
    # 其余（S / . / 空格 / ^ / ? / !）均为 NOP，保持 action='move'

    state.ticks += 1
    return ev


def run(program: Program, L_in: int = 0, R_in: int = 0,
        max_ticks: int | None = None, on_event=None) -> int:
    """运行程序直到 HALT，返回最终 L（doc §38）。

    max_ticks：调试用上限（None = 不限）；超限抛 MaxTicksExceeded。
    on_event：每 tick 回调一个事件 dict（用于 trace / 可视化）。
    """
    state = State(program, L_in, R_in)
    while True:
        if max_ticks is not None and state.ticks >= max_ticks:
            raise MaxTicksExceeded(
                f"达到调试上限 max_ticks={max_ticks}"
                "（注意：这不属于 XFeng 语言语义，doc §31）"
            )
        ev = step(state, program)
        if on_event is not None:
            on_event(ev)
        if ev["action"] == "halt":
            return ev["result"]
