"""XFeng 解释器单元测试。

覆盖 doc.md 中的规范示例、错误分类与边界行为。
运行：python -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from xfeng.errors import (
    BoundaryError,
    InvalidProgram,
    MaxTicksExceeded,
    UndefinedFunction,
)
from xfeng.interpreter import run
from xfeng.parser import parse_source


def run_src(src, L=0, R=0, max_ticks=None):
    return run(parse_source(src), L_in=L, R_in=R, max_ticks=max_ticks)


class TestParse(unittest.TestCase):
    """doc §2–§6、§39.1–§39.2：语法与校验。"""

    def test_minimal(self):
        prog = parse_source("@main\nSE")
        self.assertEqual(len(prog.functions), 1)
        self.assertIsNotNone(prog.main)
        self.assertEqual(prog.main.width, 2)
        self.assertEqual(prog.main.spawn, (0, 0))
        self.assertEqual(prog.main.exit, (1, 0))

    def test_comments_ignored(self):
        prog = parse_source("# 头注释\n@main\nSE\n# 尾注释")
        self.assertIsNotNone(prog.main)
        self.assertEqual(prog.main.height, 1)
        self.assertEqual(prog.main.width, 2)

    def test_multiple_functions(self):
        prog = parse_source("@main\nSFE\n@F\nS(E")
        self.assertIn("F", prog.functions)
        self.assertEqual(len(prog.functions), 2)

    def test_map_rectangular_ok(self):
        parse_source("@main\nS..\n...\n..E")

    def test_blank_line_invalid(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@main\nSE\n\n")

    def test_single_trailing_newline_ok(self):
        # 文件末尾单个换行符（普通文本文件）不算空行
        prog = parse_source("@main\nSE\n")
        self.assertIsNotNone(prog.main)

    def test_non_rectangular_invalid(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@main\nSE\nS..")

    def test_missing_main(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@F\nSE")

    def test_duplicate_main(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@main\nSE\n@main\nSE")

    def test_duplicate_function(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@main\nSE\n@F\nSE\n@F\nSE")

    def test_empty_map(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@main\n@F\nSE")

    def test_empty_map_only_comments(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@main\nSE\n@F\n# 注释不算地图")

    def test_missing_s(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@main\n.E")

    def test_missing_e(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@main\nS.")

    def test_multiple_s(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@main\nSSE")

    def test_multiple_e(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@main\nSEE")

    def test_reserved_future_char_plus(self):
        # `+ - ~ v` 满足函数名候选规则（非保留/非空白/非 @#），
        # 未声明时按「未定义函数」处理（见 README「规范澄清」）
        with self.assertRaises(UndefinedFunction):
            parse_source("@main\nS+E")

    def test_illegal_char_at(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@main\nS@E")

    def test_illegal_char_tab(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@main\nS\tE")

    def test_undefined_function(self):
        with self.assertRaises(UndefinedFunction):
            parse_source("@main\nSFE")

    def test_undefined_unicode_name(self):
        with self.assertRaises(UndefinedFunction):
            parse_source("@main\nS加E")

    def test_decl_trailing_space_invalid(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@main \nSE")

    def test_decl_indented_is_map_content(self):
        # doc §2.2：行首空格则 @ 属于地图正文 → '@' 非法
        with self.assertRaises(InvalidProgram):
            parse_source("@main\n  @F")

    def test_case_sensitive_names(self):
        # doc §5 文字与示例矛盾：按示例实现为大小写敏感
        prog = parse_source("@main\nSAaE\n@A\nSE\n@a\nSE")
        self.assertIn("A", prog.functions)
        self.assertIn("a", prog.functions)
        self.assertIsNot(prog.functions["A"], prog.functions["a"])

    def test_duplicate_same_case_invalid(self):
        with self.assertRaises(InvalidProgram):
            parse_source("@main\nSAE\n@A\nSE\n@A\nSE")

    def test_unicode_function_name(self):
        prog = parse_source("@main\nS加E\n@加\nSE")
        self.assertIn("加", prog.functions)

    def test_content_before_decl_invalid(self):
        with self.assertRaises(InvalidProgram):
            parse_source("SE\n@main\nSE")

    def test_bom_ok(self):
        prog = parse_source("\ufeff@main\nSE")
        self.assertIsNotNone(prog.main)


class TestExecute(unittest.TestCase):
    """doc §41–§45 等示例与核心语义。"""

    def test_minimal_program(self):  # doc §41
        self.assertEqual(run_src("@main\nSE", L=5), 5)
        self.assertEqual(run_src("@main\nSE"), 0)

    def test_resource_program(self):  # doc §42
        self.assertEqual(run_src("@main\nS(E"), 1)

    def test_counter(self):
        self.assertEqual(run_src("@main\nS((((E"), 4)

    def test_direction(self):  # doc §43
        self.assertEqual(run_src("@main\nS>E"), 0)

    def test_function(self):  # doc §44
        self.assertEqual(run_src("@main\nSFE\n@F\nS(E"), 1)

    def test_function_h_change_boundary(self):  # doc §45
        # F 把 h 改成 -1，返回后主程序从 F 向左走，最终越界
        with self.assertRaises(BoundaryError):
            run_src("@main\nSFE\n@F\nS<E")

    def test_gate_nonzero(self):
        self.assertEqual(run_src("@main\nS(?E"), 1)

    def test_gate_zero_drop_to_e(self):
        self.assertEqual(run_src("@main\nS?.\n.E."), 0)

    def test_gate_zero_drop_out(self):  # doc §19
        with self.assertRaises(BoundaryError):
            run_src("@main\nS?E")

    def test_right_gate_zero_drops(self):
        with self.assertRaises(BoundaryError):
            run_src("@main\nS!E", R=0)

    def test_right_gate_nonzero(self):
        self.assertEqual(run_src("@main\nS!E", R=5), 0)

    def test_gate_delayed_one_tick(self):  # doc §17：门判定在下一 tick
        events = []
        run(parse_source("@main\nS?.\n.E."), on_event=lambda e: events.append(e))
        self.assertEqual(len(events), 2)  # tick0: S→?；tick1: ?→E(halt)
        self.assertEqual(events[-1]["action"], "halt")
        self.assertEqual(events[-1]["result"], 0)

    def test_fall_and_ladder(self):
        self.assertEqual(run_src("@main\nS...E\n ..^ "), 0)
        self.assertEqual(run_src("@main\nS .\n . \n  E"), 0)

    def test_turnaround(self):
        self.assertEqual(run_src("@main\nS.. \n ..<\nE..."), 0)

    def test_s_revisit_nop(self):
        # doc §7：重新走到 S 无特殊行为；h=-1 后向左越界
        with self.assertRaises(BoundaryError):
            run_src("@main\nS.<E")

    def test_function_modifies_resources_persist(self):
        # 函数内 L 修改返回后保留（doc §22）
        self.assertEqual(run_src("@main\nSF.E\n@F\nS()]E"), 1)

    def test_recursion_halts(self):
        self.assertEqual(run_src(
            "@main\nS...F..E\n@F\nS[?F.E\n  ...^", L=3), 0)

    def test_recursion_stack_depth(self):
        depths = []
        run(parse_source("@main\nS...F..E\n@F\nS[?F.E\n  ...^"),
            L_in=3, on_event=lambda e: depths.append(e["depth"]))
        self.assertEqual(max(depths), 3)

    def test_recursion_infinite_hits_max_ticks(self):
        # L=0 时 `[` 把 L 变成 -1，? 恒为非零 → 无限递归
        with self.assertRaises(MaxTicksExceeded):
            run_src("@main\nS...F..E\n@F\nS[?F.E\n  ...^", L=0, max_ticks=1000)

    def test_infinite_loop_hits_max_ticks(self):
        # S><E：在 > 和 < 之间来回，永不终止
        with self.assertRaises(MaxTicksExceeded):
            run_src("@main\nS><E", max_ticks=100)

    def test_return_does_not_reexecute_call_point(self):
        # 若返回后重新执行 F，会无限调用；能 HALT 即证明不重执行（doc §27）
        self.assertEqual(run_src("@main\nSFE\n@F\nS(E"), 1)


class TestFibonacci(unittest.TestCase):
    """examples/fib.xfeng：(n,0) -> (F_n,0)。"""

    FIB = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]

    @classmethod
    def setUpClass(cls):
        from pathlib import Path
        src = Path(__file__).resolve().parent.parent / "examples" / "fib.xfeng"
        cls.prog = parse_source(src.read_text(encoding="utf-8"))

    def test_fib_values(self):
        for n, expected in enumerate(self.FIB):
            self.assertEqual(
                run(self.prog, L_in=n), expected,
                f"F_{n} 应为 {expected}",
            )

    def test_fib_final_state(self):
        # 最终状态应为 (L,R)=(F_n,0)
        from xfeng.interpreter import State, step
        for n, expected in ((0, 0), (1, 1), (6, 8), (12, 144)):
            st = State(self.prog, L_in=n)
            while True:
                ev = step(st, self.prog)
                if ev["action"] == "halt":
                    break
            self.assertEqual((st.L, st.R), (expected, 0))


if __name__ == "__main__":
    unittest.main()
