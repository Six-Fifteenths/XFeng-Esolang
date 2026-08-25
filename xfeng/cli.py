"""XFeng 1.0 命令行解释器入口。"""

import argparse
import json
import sys
from pathlib import Path

from .errors import XFengError
from .interpreter import dir_name, run
from .parser import parse_source


def _format_event(ev: dict) -> str:
    h = "+1" if ev["h"] == 1 else "-1"
    head = (
        f"tick={ev['tick']:05d} @{ev['map']} ({ev['x']},{ev['y']}) "
        f"{ev['cell']!r} L={ev['L']} R={ev['R']} h={h} depth={ev['depth']}"
    )
    action = ev.get("action")
    if action == "halt":
        return (f"{head} → {dir_name(ev.get('dir'))} → ({ev['to'][0]},{ev['to'][1]}) "
                f"{ev['arrived']!r} → HALT，输出 L = {ev['result']}")
    if action == "return":
        return (f"{head} → {dir_name(ev.get('dir'))} → ({ev['to'][0]},{ev['to'][1]}) "
                f"{ev['arrived']!r} → 返回 @{ev['to_map']} {ev['call_point']}")
    d = ev.get("dir")
    if action == "call":
        return (f"{head} → {dir_name(d)} → ({ev['to'][0]},{ev['to'][1]}) "
                f"{ev['arrived']!r} → 调用 {ev['callee']} → @{ev['callee_map']} "
                f"{ev['callee_spawn']}（S）")
    return f"{head} → {dir_name(d)} → ({ev['to'][0]},{ev['to'][1]}) {ev['arrived']!r}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="xfeng",
        description="XFeng 1.0 解释器（二维空间控制流 esolang，见 doc.md）",
        epilog="示例：python -m xfeng examples/recursion.xfeng -l 3 --trace",
    )
    ap.add_argument("program", help="XFeng 源文件路径，或 '-' 表示从标准输入读取")
    ap.add_argument("-l", "--L", type=int, default=0, help="初始 L（默认 0）")
    ap.add_argument("-r", "--R", type=int, default=0, help="初始 R（默认 0）")
    ap.add_argument(
        "-t", "--max-ticks", type=int, default=None,
        help="调试用最大 tick 数（注意：不属于语言语义，doc §31）",
    )
    ap.add_argument("--trace", action="store_true", help="打印逐步执行追踪")
    ap.add_argument("--check", action="store_true", help="只校验程序，不执行")
    ap.add_argument(
        "--json", action="store_true",
        help="以 JSON 输出结果（便于脚本 / 测试）",
    )
    args = ap.parse_args(argv)

    try:
        if args.program == "-":
            text = sys.stdin.read()
        else:
            text = Path(args.program).read_text(encoding="utf-8")
    except OSError as e:
        print(f"读取文件失败：{e}", file=sys.stderr)
        return 2

    def _emit_error(e: XFengError) -> int:
        if args.json:
            print(json.dumps(
                {"status": "error", "kind": e.kind, "message": e.message},
                ensure_ascii=False,
            ))
        else:
            print(str(e), file=sys.stderr)
        return 1

    try:
        prog = parse_source(text)
    except XFengError as e:
        return _emit_error(e)

    if args.check:
        if args.json:
            print(json.dumps(
                {"status": "ok", "functions": [n for n, _ in prog.order]},
                ensure_ascii=False,
            ))
        else:
            print(f"OK：程序合法（{len(prog.order)} 个程序段）")
        return 0

    try:
        result = run(
            prog, args.L, args.R, args.max_ticks,
            on_event=(lambda ev: print(_format_event(ev))) if args.trace else None,
        )
    except XFengError as e:
        return _emit_error(e)

    if args.json:
        print(json.dumps({"status": "ok", "result": result}, ensure_ascii=False))
    else:
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
