#!/usr/bin/env python3
"""一键生成 XFeng 网页 IDE（支持打开 .xfeng / 在线编辑并运行）。

用法：
    python compile.py                         # 生成 ide.html（内置示例）
    python compile.py program.xfeng           # 生成预加载该程序的 IDE 页
    python compile.py program.xfeng -o out.html --title 标题

等价于：python -m htmlc [program] [-o <out>] [--title <标题>]
"""
import sys

from htmlc.compiler import main

if __name__ == "__main__":
    sys.exit(main())
