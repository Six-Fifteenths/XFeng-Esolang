# XFeng 1.0 · 练起来

> **「欢迎来到 XFeng 编程世界，我是你的规划导师张雪峰。」**

一门**二维空间控制流** esolang：Agent「张雪峰」在矩形地图上逐格奔跑——左手巧乐兹（`L`）、
右手雪碧（`R`），沿「文理方向」（`h`）一路跑向「上岸」（`E`）。

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![CI](https://img.shields.io/github/actions/workflow/status/Six-Fifteenths/XFeng-Esolang/ci.yml?label=CI)](.github/workflows/ci.yml)

## 这是什么

每个 tick 严格执行：

> **当前格决定方向 → 移动一格 → 执行到达格**

- 地图字符同时承担**执行语义**（到达后修改程序状态）与**运动语义**（决定下一步怎么走）；
- 核心状态 `Σ=(P,x,y,h,L,R,C)`：地图、坐标、水平朝向 `h∈{-1,+1}`、整数资源 `L,R∈ℤ`、调用栈；
- 支持**函数 / 递归 / 相互递归**：调用栈只保存「(调用者地图, 调用点)」，`L,R,h` 全程共享，函数返回后**不恢复 `h`**；
- **严格确定性**：无随机、无隐式规则（不反弹、不穿墙、不环绕、不自动判死循环）；主程序到达 `E` 输出 `L`。

正式规范见 [`doc.md`](doc.md)（含运动函数 `D(c,L,R,h)` 与执行函数 `Exec` 的完整定义）。

### 梗对照表

| 语言概念      | 张雪峰梗          | 技术含义                                     |
| ------------- | ----------------- | -------------------------------------------- |
| Agent         | 张雪峰老师        | 执行指针，逐格奔跑                           |
| `L` / `R` | 巧乐兹 / 雪碧     | 整数资源（寄存器）                           |
| `h`         | 文理方向          | 水平朝向`+1` / `-1`                      |
| `S`         | 高考考场          | 出生点                                       |
| `E`         | 成功上岸          | 主程序停机（输出 L）/ 函数返回               |
| `?` / `!` | 考研线 / 专业门槛 | L/R 归零 → 下沉`(0,1)`；否则沿 `h` 平移 |
| 空格 /`^`   | 下沉市场 / 专升本 | 自由落体 / 爬梯                              |
| `<` / `>` | 报考调剂          | 强制转向`h=−1` / `h=+1`                 |

---

## 快速开始

需要 Python 3.10+（纯标准库，零第三方依赖）。

```bash
# 运行程序，打印最终 L
python -m xfeng examples/fib.xfeng -l 6        # → 8
python -m xfeng examples/nth-prime.xfeng -l 10  # → 29

# 逐步追踪 / 只校验
python -m xfeng examples/gate-zero.xfeng --trace
python -m xfeng examples/hchange.xfeng --check

# 指定初始 L/R 与调试上限
python -m xfeng examples/min.xfeng -l 42
python -m xfeng examples/recursion.xfeng -l 0 -t 1000   # 无限递归 → MaxTicksExceeded
```

（可选）安装为命令行工具：

```bash
pip install -e .
xfeng examples/fib.xfeng -l 6
```

## 网页 IDE（`ide.html`）

仓库自带 **`ide.html`**——一个完全自包含的网页 IDE（内嵌 JS 解析器 + 解释器 + 编辑器），
无需 Python、无需构建，**双击打开即可使用**，也可上传到任意静态托管：

- **📂 打开 / 拖拽** `.xfeng` 文件，或从内置示例下拉切换（min / gate / recursion / fib / **nth-prime**…）；
- **在线编辑**，边写边实时语法校验、报错定位；
- **解析 → 校验 → 运行**：逐格渲染所有函数地图，张雪峰 🏃 逐格奔跑动画（函数调用传送特效、停机「成功上岸」庆祝），L/R/h/tick/调用栈实时面板；
- 单步 / 运行 / 暂停 / 重置、速度控制、执行日志。

---

## 示例程序

| 文件                  | 说明                                          | 结果                          |
| --------------------- | --------------------------------------------- | ----------------------------- |
| `min.xfeng`         | 最小程序（doc §41）                          | 输出`L_in`                  |
| `resource.xfeng`    | 资源程序（doc §42）                          | `1`                         |
| `counter.xfeng`     | 连续`(`（巧乐兹 +4）                        | `4`                         |
| `direction.xfeng`   | 方向程序（doc §43）                          | `0`                         |
| `function.xfeng`    | 函数程序（doc §44）                          | `1`                         |
| `hchange.xfeng`     | 函数改 h（doc §45）                          | `BoundaryError`（向左越界） |
| `gate.xfeng`        | `?` 门，L≠0 通过                           | `1`                         |
| `gate-zero.xfeng`   | `?` 门，L=0 下沉                            | `0`                         |
| `fall.xfeng`        | 自由落体三段                                  | `0`                         |
| `fall-ladder.xfeng` | 下沉 +`^` 攀升                              | `0`                         |
| `turnaround.xfeng`  | `<` 转向 + 落体                             | `0`                         |
| `recursion.xfeng`   | 递归递减至 0                                  | `0`（L=3 时，深度 3）       |
| `fib.xfeng`         | **斐波那契**：(n,0) → (F_n,0)          | `F_n`（如 n=6 → 8）        |
| `nth-prime.xfeng`   | **第 n 个质数**：(n,0) → (p_n,0)，n≥1 | `p_n`（如 n=100 → 541）    |

`fib.xfeng` 是 doc §46 的斐波那契程序，由 4 个函数组成：`main` 依次调用 `M`（把 n 从 L 搬到 R）、
`F`（递归树遍历，每个 `fib(1)` 叶子给 L+1）、`C`（清零 R）。`F` 的不变量：调用时 `R=level`，
返回时 R 恢复且 `L += F_level`。Python 与 JS 双引擎对 n=6 交叉验证一致（483 tick，输出 8）。

`nth-prime.xfeng` 是运行时算法（朴素试除），不是质数表。`F` 用普通递归深度保存 `n`，每次返回
调用 `X` 寻找下一个候选数；`D` 用可逆递归减法判断整除（`B` 已并入 `D`，`a` 已并入 `A`），
`K` 只有在最小除数等于候选数本身时才判为质数。非注释部分 41 行，最长一行 14 字符，9 个函数。
标准逐步解释器适合观察较小输入；单元测试对 `n=1..15` 做了精确质数回归覆盖。

---

## 命令行参考

### 解释器 `python -m xfeng`

| 选项                  | 说明                                                     |
| --------------------- | -------------------------------------------------------- |
| `program`           | 源文件路径，或`-`（读 stdin）                          |
| `-l, --L N`         | 初始 L（默认 0）                                         |
| `-r, --R N`         | 初始 R（默认 0）                                         |
| `-t, --max-ticks N` | 调试用最大 tick 数（**不属于语言语义**，doc §31） |
| `--trace`           | 打印逐步追踪                                             |
| `--check`           | 只校验，不执行                                           |
| `--json`            | 机器可读输出                                             |

退出码：`0` 成功 HALT / 校验通过；`1` XFeng 错误；`2` 使用错误。

---

## 测试

```bash
python -m unittest discover -s tests -v
# 或
make test
```

## 错误分类（与 doc §39 对应）

| 错误                  | 触发                                                                            |
| --------------------- | ------------------------------------------------------------------------------- |
| `InvalidProgram`    | 缺/多`@main`、重复声明、空/非矩形地图、缺或多 `S`/`E`、非法字符、非法声明 |
| `UndefinedFunction` | 地图出现合法函数名字符但无对应声明                                              |
| `BoundaryError`     | Agent 越界（不反弹 / 不穿墙 / 不环绕）                                          |
| `MaxTicksExceeded`  | （调试限制，非语言语义）                                                        |

---

## 项目结构

```text
XFeng/
├─ doc.md                  # 语言规范
├─ README.md
├─ ide.html                # 网页 IDE（自包含，双击打开即用）
├─ LICENSE                 # MIT
├─ pyproject.toml          # 打包配置（pip install -e . 后可装出 xfeng 命令）
├─ Makefile                # make test / make check / make clean
├─ xfeng/                  # 解释器包
│  ├─ errors.py            # 错误分类
│  ├─ parser.py            # 解析与校验
│  ├─ interpreter.py       # 执行引擎（State / step / run）
│  ├─ cli.py               # 命令行入口
│  └─ __main__.py
├─ examples/               # 示例程序（*.xfeng）
├─ tests/                  # 单元测试
└─ .github/workflows/      # GitHub Actions CI（跑测试 + 冒烟执行）
```

## 致谢与致敬

`nth-prime.xfeng`（第 n 个质数）的诞生离不开两位 AI 助手的协作：

- **ChatGPT**：提出「对称退栈恢复电路」方案——以 `h` 兼任布尔结果通道、用可逆递归恢复
  寄存器，解决了双寄存器 + 调用栈限制下多参数函数的寄存器污染问题。
- **DeepSeek**：完成方案的 XFeng 落地实现、Python/JS 双引擎逐 tick 交叉验证，
  以及 41 行 / 14 字符的行数优化与验证文档整理。

致敬张雪峰老师——「练起来」来自张老师在办公室跑步机上的名场面（"在公司咱们就练起来！"），
也是这门「张雪峰跑步」语言最好的注脚：**跑不停，算不停。我们永远记得你。**

## License

MIT License · © 2026 XFeng contributors
