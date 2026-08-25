"""Exact accelerated verifier for examples/nth-prime.xfeng.

Numba changes execution speed, not XFeng semantics.  The verifier executes every
tick and compares the 500 prime checkpoints with an independent Eratosthenes
sieve.  It is deliberately separate from the dependency-free interpreter.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from numba import njit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from xfeng.parser import parse_source


DOT, SPACE, UP, QL, QR = 0, 1, 2, 3, 4
INC_L, DEC_L, INC_R, DEC_R = 5, 6, 7, 8
LEFT, RIGHT, START, END, CALL_BASE = 9, 10, 11, 12, 100


def compile_program(source: str):
    program = parse_source(source)
    maps = [item for _, item in program.order]
    ids = {item.name: i for i, item in enumerate(maps)}
    height = max(item.height for item in maps)
    width = max(item.width for item in maps)
    cells = np.full((len(maps), height, width), DOT, dtype=np.int16)
    widths = np.array([item.width for item in maps], dtype=np.int32)
    heights = np.array([item.height for item in maps], dtype=np.int32)
    spawns = np.array([item.spawn for item in maps], dtype=np.int32)
    basic = {
        ".": DOT, " ": SPACE, "^": UP, "?": QL, "!": QR,
        "(": INC_L, "[": DEC_L, ")": INC_R, "]": DEC_R,
        "<": LEFT, ">": RIGHT, "S": START, "E": END,
    }
    for map_id, item in enumerate(maps):
        for y, row in enumerate(item.rows):
            for x, char in enumerate(row):
                if char in basic:
                    cells[map_id, y, x] = basic[char]
                else:
                    cells[map_id, y, x] = CALL_BASE + ids[char]
    return cells, widths, heights, spawns, ids


@njit(cache=True)
def fast_run(cells, widths, heights, spawns, main_id, x_id, f_id,
             left, right, max_ticks, capture_count):
    stack_map = np.empty(1_000_000, dtype=np.int32)
    stack_x = np.empty(1_000_000, dtype=np.int32)
    stack_y = np.empty(1_000_000, dtype=np.int32)
    captured = np.empty(capture_count, dtype=np.int64)
    captured_n = 0
    current = main_id
    x, y = spawns[current, 0], spawns[current, 1]
    h, depth, ticks, max_depth = 1, 0, 0, 0
    max_abs = max(abs(left), abs(right))
    while ticks < max_ticks:
        char = cells[current, y, x]
        if char == SPACE:
            dx, dy = 0, 1
        elif char == UP:
            dx, dy = 0, -1
        elif char == QL and left == 0:
            dx, dy = 0, 1
        elif char == QR and right == 0:
            dx, dy = 0, 1
        else:
            dx, dy = h, 0
        x, y = x + dx, y + dy
        if x < 0 or x >= widths[current] or y < 0 or y >= heights[current]:
            return -1, left, right, ticks, captured[:captured_n], max_depth, max_abs
        arrived = cells[current, y, x]
        if arrived == END:
            if current == main_id:
                return 1, left, right, ticks + 1, captured[:captured_n], max_depth, max_abs
            if current == x_id and stack_map[depth - 1] == f_id:
                if captured_n < capture_count:
                    captured[captured_n] = left
                    captured_n += 1
            depth -= 1
            current, x, y = stack_map[depth], stack_x[depth], stack_y[depth]
        elif arrived == INC_L:
            left += 1
        elif arrived == DEC_L:
            left -= 1
        elif arrived == INC_R:
            right += 1
        elif arrived == DEC_R:
            right -= 1
        elif arrived == LEFT:
            h = -1
        elif arrived == RIGHT:
            h = 1
        elif arrived >= CALL_BASE:
            stack_map[depth], stack_x[depth], stack_y[depth] = current, x, y
            depth += 1
            if depth > max_depth:
                max_depth = depth
            current = arrived - CALL_BASE
            x, y = spawns[current, 0], spawns[current, 1]
        value = max(abs(left), abs(right))
        if value > max_abs:
            max_abs = value
        ticks += 1
    return 0, left, right, ticks, captured[:captured_n], max_depth, max_abs


def reference_primes(count: int) -> list[int]:
    if count < 1:
        return []
    limit = 16 if count < 6 else int(count * (math.log(count) + math.log(math.log(count)))) + 16
    while True:
        sieve = bytearray(b"\x01") * (limit + 1)
        sieve[:2] = b"\x00\x00"
        for value in range(2, math.isqrt(limit) + 1):
            if sieve[value]:
                start = value * value
                sieve[start::value] = b"\x00" * (((limit - start) // value) + 1)
        result = [i for i, flag in enumerate(sieve) if flag]
        if len(result) >= count:
            return result[:count]
        limit *= 2


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--max-ticks", type=int, default=100_000_000_000)
    parser.add_argument("--result", type=Path)
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be positive")

    source_path = ROOT / "examples" / "nth-prime.xfeng"
    source = source_path.read_text(encoding="utf-8")
    code_lines = [line for line in source.splitlines() if not line.startswith("#")]
    assert len(code_lines) <= 50
    assert max(map(len, code_lines)) <= 50
    cells, widths, heights, spawns, ids = compile_program(source)
    started = time.perf_counter()
    status, left, right, ticks, values, max_depth, max_abs = fast_run(
        cells, widths, heights, spawns,
        ids["main"], ids["X"], ids["F"],
        args.count, 0, args.max_ticks, args.count,
    )
    elapsed = time.perf_counter() - started
    expected = reference_primes(args.count)
    actual = values.tolist()
    assert status == 1, f"XFeng status={status}, ticks={ticks}"
    assert (left, right) == (expected[-1], 0)
    assert actual == expected
    result = {
        "input": [args.count, 0],
        "output": int(left),
        "right_register": int(right),
        "xfeng_ticks": int(ticks),
        "checkpoint_count": len(actual),
        "reference": "independent exact Eratosthenes sieve",
        "all_checkpoints_match": True,
        "max_call_depth": int(max_depth),
        "max_absolute_register": int(max_abs),
        "source_non_comment_lines": len(code_lines),
        "source_max_line_length": max(map(len, code_lines)),
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "elapsed_seconds": elapsed,
        "python": sys.version.split()[0],
        "numpy": np.__version__,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.result:
        path = args.result if args.result.is_absolute() else ROOT / args.result
        path.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
