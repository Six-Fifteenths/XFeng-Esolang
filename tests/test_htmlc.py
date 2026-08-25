"""HTML 编译器（网页 IDE）单元测试。"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from htmlc.compiler import compile_source


class TestCompile(unittest.TestCase):
    def test_valid_program(self):
        html, valid, fatal = compile_source("@main\nS(E", "test")
        self.assertTrue(valid)
        self.assertIsNone(fatal)
        self.assertIn("<html", html)
        self.assertIn("</html>", html)
        # 源码被预加载进编辑器
        self.assertIn("S(E", html)
        # IDE 组件齐全
        self.assertIn("id=\"editor\"", html)
        self.assertIn("fileInput", html)
        self.assertIn("parseSource", html)
        # 不应残留占位符
        self.assertNotIn("__SOURCE_JSON__", html)
        self.assertNotIn("__TITLE_JSON__", html)
        self.assertNotIn("__PROGNAME__", html)

    def test_no_program_uses_default(self):
        html, valid, fatal = compile_source(None, "IDE")
        self.assertTrue(valid)
        self.assertIsNone(fatal)
        self.assertIn("@main", html)

    def test_invalid_program(self):
        html, valid, fatal = compile_source("@main\nSE\n\n", "test")
        self.assertFalse(valid)
        self.assertIn("InvalidProgram", fatal)
        self.assertIn("parseError", html)

    def test_undefined_function(self):
        html, valid, fatal = compile_source("@main\nSFE", "t")
        self.assertFalse(valid)
        self.assertIn("UndefinedFunction", fatal)

    def test_source_script_injection_escaped(self):
        # 源码里的 </script> 必须转义，不能破坏页面
        html, valid, fatal = compile_source("@main\n# </script>\nSE", "x")
        self.assertTrue(valid)
        self.assertIn("\\u003c/script\\u003e", html)
        self.assertNotIn("</script>#", html)

    def test_lt_char_safe(self):
        # 地图里的 < > 以 unicode 转义内嵌，避免破坏 script 块
        html, valid, fatal = compile_source("@main\nS<...E", "x")
        self.assertTrue(valid)
        self.assertIn("\\u003c", html)

    def test_unicode_function_name(self):
        html, valid, fatal = compile_source("@main\nS加E\n@加\nSE", "加")
        self.assertTrue(valid)
        self.assertIn("加", html)


if __name__ == "__main__":
    unittest.main()
