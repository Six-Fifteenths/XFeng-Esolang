"""XFeng → 网页 IDE（HTML）生成器。

生成一个完全自包含的网页 IDE：
  - 直接打开 .xfeng 文件（文件选择 / 拖拽进编辑器）；
  - 在线编辑 XFeng 源码；
  - 浏览器内解析 / 校验 / 运行 / 可视化（内嵌 JS 解析器 + 解释器）。
"""

import argparse
import json
import sys
from pathlib import Path

# 确保能导入仓库根目录的 xfeng 包（用于 CLI 退出码校验）
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from xfeng.errors import XFengError  # noqa: E402
from xfeng.parser import parse_source  # noqa: E402

TEMPLATE = Path(__file__).resolve().parent / "template.html"

#: 无程序参数时 IDE 预加载的内置示例（递归递减至 0）
DEFAULT_EXAMPLE = "@main\nS...F..E\n@F\nS[?F.E\n  ...^"


def escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def js_string(s: str) -> str:
    """把字符串编码为安全的 JS 字符串字面量。

    < > & 转义为 unicode 转义，避免 `</script>` 之类的序列破坏页面。
    """
    return (
        json.dumps(s, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def compile_source(source: str | None = None, title: str = "XFeng IDE"):
    """生成 IDE 页 → (html, valid, fatal_message)。

    source 为 None 时使用内置默认示例。页面始终是完整的网页 IDE：
    JS 端负责运行时解析与校验，因此即使预加载的程序非法，页面也能编辑修正。
    CLI 退出码仍以 Python 端校验为准。
    """
    if source is None:
        source = DEFAULT_EXAMPLE
    try:
        parse_source(source)
        fatal = None
        valid = True
    except XFengError as e:
        fatal = f"{e.kind}: {e.message}" + (f"（第 {e.line} 行）" if e.line else "")
        valid = False

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("__PROGNAME__", escape_html(title))
    html = html.replace("__SOURCE_JSON__", js_string(source))
    html = html.replace("__TITLE_JSON__", js_string(title))
    return html, valid, fatal


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="htmlc",
        description="生成 XFeng 网页 IDE：可直接打开 .xfeng 文件或在线编辑代码，并在浏览器内编译运行",
        epilog=(
            "示例：python -m htmlc                       # 生成 ide.html（内置示例）\n"
            "      python -m htmlc examples/fib.xfeng   # 生成预加载该程序的 IDE 页"
        ),
    )
    ap.add_argument(
        "program", nargs="?", default=None,
        help="要预加载的 .xfeng 源文件（可选）",
    )
    ap.add_argument(
        "-o", "--output", default=None,
        help="输出 HTML 路径（默认 <输入名>.html 或 ide.html）",
    )
    ap.add_argument(
        "--title", default=None,
        help="页面标题（默认取文件名或 XFeng IDE）",
    )
    args = ap.parse_args(argv)

    if args.program:
        src = Path(args.program)
        try:
            source = src.read_text(encoding="utf-8")
        except OSError as e:
            print(f"读取文件失败：{e}", file=sys.stderr)
            return 2
        title = args.title or src.stem
        out = Path(args.output) if args.output else src.with_suffix(".html")
    else:
        source = None
        title = args.title or "XFeng IDE"
        out = Path(args.output) if args.output else Path("ide.html")

    html, valid, fatal = compile_source(source, title)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    if valid:
        print(f"✔ 已生成 {out}（{len(html)} 字节）")
        return 0
    print(f"✘ 预加载程序无效：{fatal}", file=sys.stderr)
    print(f"（页面仍可打开并编辑修正：{out}）", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
