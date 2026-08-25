# XFeng 1.0 · 练起来

> **「欢迎来到 XFeng 编程世界，我是你的规划导师张雪峰。」**

一个**二维空间控制流** esolang：Agent「张雪峰」在矩形地图上奔跑——左手巧乐兹（$L$）、
右手雪碧（$R$），沿着**文理方向**（$h$，$+1$ 理科 / $-1$ 文科）一路跑向「上岸」（$E$）。
踩到 `?`/`!` 门槛就低头看看手里有没有积压：**归零直接下沉，非零继续冲。**

**别愣着，练起来！**——这门语言本身就是「张雪峰跑步」：每一格都要跑，每一步都要算。

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![CI](https://img.shields.io/github/actions/workflow/status/YOUR_GITHUB_USER/YOUR_REPO/ci.yml?label=CI)](.github/workflows/ci.yml)
<!-- ↑ 上传到 GitHub 后，把 YOUR_GITHUB_USER / YOUR_REPO 替换成你的仓库地址 -->

---

## 梗对照表 · 练起来

| 语言概念 | 张雪峰梗 | 技术含义 |
|---|---|---|
| Agent | **张雪峰老师**（在公司咱们就练起来） | 执行指针 / 状态机，在地图上逐格奔跑 |
| $L$ | **巧乐兹** | 左手资源，整数计数器 |
| $R$ | **雪碧** | 右手资源，整数计数器 |
| $h$ | **文理方向**（$+1$ 理科 / $-1$ 文科） | 水平朝向 |
| `S` | 高考考场 / 报志愿 | 出生点（启动时放置 Agent） |
| `E` | **成功上岸** | 主程序 → 停机（输出 L）；函数 → 返回 |
| `?` / `!` | 考研线 / 专业门槛 | L / R 归零 → 下沉 $(0,1)$；否则沿 $h$ 平移 |
| 空格 / `^` | 下沉市场 / 专升本 | 自由落体 / 爬梯 |
| `<` / `>` | 报考调剂 | 强制转向（$h\gets-1$ / $h\gets+1$） |

> **张老师语录（认真版）：**
> **选择比努力更重要**——选对每一个字符，张老师带你上岸。
> **普通家庭别谈情怀，先谈能不能 HALT。**
> **家里没矿别硬刚，先看看地图边界在哪。**
> **别愣着，练起来！**

---

## 正经介绍 · 这是什么

XFeng 是一张人生地图，也是一门**严格确定性**的形式化语言。每个 tick 严格执行：

$$\boxed{\text{根据当前格确定下一步方向} \rightarrow \text{移动一格} \rightarrow \text{执行到达格}}$$

- 地图字符同时承担**执行语义**（到达后修改程序状态）与**运动语义**（决定下一步怎么走）；
- 核心状态 $\Sigma=(P,x,y,h,L,R,C)$：当前地图、坐标、水平朝向、两个整数资源 $L,R\in\mathbb{Z}$、调用栈；
- 支持**函数调用 / 递归 / 相互递归**：调用栈只保存「(调用者地图, 调用点)」，$L,R,h$ 全程共享，函数返回后**不恢复** $h$；
- **确定性**：给定源文件 + 初始 $(L,R)$，运行轨迹唯一——没有随机、没有隐式规则（不反弹、不穿墙、不环绕、不自动检测死循环）；
- 主程序到达 `E` 输出 $L$（即「上岸」时的巧乐兹结余）。

正式规范见 [`doc.md`](doc.md)——包含运动函数 $D(c,L,R,h)$ 与执行函数 $\operatorname{Exec}$ 的完整定义。

本项目包含两大部分：

1. **`xfeng/`** — Python 解释器（解析 / 校验 / 执行）
2. **`htmlc/`** — XFeng → 网页 IDE 生成器（内嵌 JS 解析器 + 解释器 + 编辑器）

---

## 快速开始

需要 Python 3.10+（仅标准库，无第三方依赖）。

```bash
# 解释器：运行程序，打印最终 L（结余巧乐兹）
python -m xfeng examples/fib.xfeng -l 6        # → 8

# 逐步追踪
python -m xfeng examples/gate-zero.xfeng --trace

# 只校验合法性
python -m xfeng examples/hchange.xfeng --check

# 指定初始 L / R 与调试上限
python -m xfeng examples/min.xfeng -l 42
python -m xfeng examples/recursion.xfeng -l 0 -t 1000   # 无限递归 → MaxTicksExceeded

# 生成网页 IDE（打开即用，内置示例）
python -m htmlc
python -m htmlc examples/fib.xfeng -o fib.html   # 或预加载某个程序
```

## 网页 IDE（编译 → 打开即用）

`htmlc` 生成的是一整个**网页 IDE**（完全自包含，无需 Python 即可在浏览器里跑）：

```bash
python -m htmlc                    # → ide.html（内置示例）
python -m htmlc 你的程序.xfeng      # → 预加载该程序的 IDE 页
python compile.py 你的程序.xfeng    # 等价写法
```

IDE 里可以：

- **📂 打开 .xfeng 文件**（或直接把文件拖进编辑器）；
- **在线编辑**代码（边写边做语法校验、实时报错）；
- 从内置示例下拉切换（min / gate / recursion / **fib 斐波那契**…）；
- 浏览器内**解析 → 校验 → 运行**：逐格地图 + 张雪峰 🏃 动画 + L/R/h/调用栈面板。

生成的 HTML 双击即可打开，也可上传到任意静态托管。

## 安装（可选）

零第三方依赖（纯标准库）：

```bash
# 方式一：直接在仓库里跑（无需安装）
python -m xfeng examples/fib.xfeng -l 6

# 方式二：pip 安装为命令行工具
pip install -e .
xfeng examples/fib.xfeng -l 6
htmlc examples/fib.xfeng
```

---

## 示例程序

| 文件 | 说明 | 结果 |
|---|---|---|
| `min.xfeng` | 最小程序（doc §41） | 输出 `L_in` |
| `resource.xfeng` | 资源程序（doc §42） | `1` |
| `counter.xfeng` | 连续 `(`（巧乐兹 +4） | `4` |
| `direction.xfeng` | 方向程序（doc §43） | `0` |
| `function.xfeng` | 函数程序（doc §44） | `1` |
| `hchange.xfeng` | 函数改 h（doc §45） | `BoundaryError`（向左越界） |
| `gate.xfeng` | `?` 门，L≠0 通过 | `1` |
| `gate-zero.xfeng` | `?` 门，L=0 下沉 | `0` |
| `fall.xfeng` | 自由落体三段 | `0` |
| `fall-ladder.xfeng` | 下沉 + `^` 攀升 | `0` |
| `turnaround.xfeng` | `<` 转向 + 落体 | `0` |
| `recursion.xfeng` | 递归递减至 0 | `0`（L=3 时，深度 3） |
| `fib.xfeng` | **斐波那契**：(n,0) → (F_n,0) | `F_n`（如 n=6 → 8） |

`fib.xfeng` 是 doc §46 提及的斐波那契程序，由 4 个函数组成：
`main` 依次调用 `M`（把 n 从 L 搬到 R）、`F`（递归树遍历，每个 `fib(1)` 叶子给 L+1）、
`C`（清零 R）。`F` 的不变量：调用时 `R=level`，返回时 R 恢复且 `L += F_level`。
Python 与 JS 双引擎对 n=6 交叉验证一致（483 tick，输出 8）。

## 可视化页 / IDE

IDE 页面采用「**练起来**」主题（跑步红 / 金榜黄 / 深蓝）。Agent「张雪峰」以跑步形象 🏃
逐格奔跑（朝左保持默认朝向、朝右翻转），运行态喊「**练起来！**」；函数调用与返回带
传送爆点特效，停机时金色「上岸」庆祝——状态栏弹出「**成功上岸！最终结余巧乐兹 L 个**」。

支持：编辑器（打开 .xfeng / 拖拽 / 内置示例 / 实时语法校验）、逐格渲染所有函数地图、
L/R/h/tick/调用栈实时面板、单步 / 运行 / 暂停 / 重置、速度控制、执行日志。

## 叙事与致敬

致敬张雪峰老师 —— **练起来，我们永远记得你**。

「练起来」来自张老师在办公室跑步机上的名场面（"在公司咱们就练起来！"）——
也是这门「张雪峰跑步」语言最好的注脚：**跑不停，算不停。**

---

## 命令行选项

### 解释器 `python -m xfeng`

| 选项 | 说明 |
|---|---|
| `program` | 源文件路径，或 `-`（读 stdin） |
| `-l, --L N` | 初始 L（默认 0） |
| `-r, --R N` | 初始 R（默认 0） |
| `-t, --max-ticks N` | 调试用最大 tick 数（**不属于语言语义**，doc §31） |
| `--trace` | 打印逐步追踪 |
| `--check` | 只校验，不执行 |
| `--json` | 机器可读输出 |

退出码：`0` 成功 HALT / 校验通过；`1` XFeng 错误；`2` 使用错误。

### HTML 编译器 `python -m htmlc`（网页 IDE）

| 选项 | 说明 |
|---|---|
| `program` | 要预加载的 .xfeng 源文件（**可选**；省略则生成内置示例的通用 IDE） |
| `-o, --output` | 输出路径（默认 `<输入名>.html` 或 `ide.html`） |
| `--title` | 页面标题（默认文件名或 XFeng IDE） |

预加载程序非法时退出码为 1（页面仍可打开并编辑修正）。

---

## 测试

```bash
python -m unittest discover -s tests -v
# 或
make test
```

## 规范澄清 / 实现决策

doc.md 个别处存在歧义，实现按以下口径处理：

1. **函数名大小写敏感**（doc §5 文字写「不区分大小写」，但示例说 `@A` 与 `@a` 是两个不同函数——按示例语义实现：区分大小写，`@A`/`@a` 可共存，同名重复声明报错）。
2. **空行 = 长度 0 的地图行**（doc §2.4）：空行出现在地图正文（含文件末尾空行）会使地图非矩形 / 宽度为 0 → `InvalidProgram`。程序末尾不要留空行。
3. **`+ - ~ v`**：满足「函数名候选」规则（非保留 / 非空白 / 非 `@#`）。未声明时在地图出现 → `UndefinedFunction`；若显式声明（如 `@+`）则可作为函数名。
4. **`max_ticks`** 只是解释器调试限制，超限抛 `MaxTicksExceeded`，**不属于** XFeng 语言语义（doc §31）。
5. **UTF-8 BOM** 自动剥离（doc §2.5 按 Unicode code point 计数）。
6. 非法字符分类：保留字符之外的普通可打印字符无声明 → `UndefinedFunction`；`@`、`#`、制表符等 → `InvalidProgram`。

## 错误分类（与 doc §39 对应）

| 错误 | 触发 |
|---|---|
| `InvalidProgram` | 缺/多 `@main`、重复声明、空/非矩形地图、缺或多 `S`/`E`、非法字符、非法声明 |
| `UndefinedFunction` | 地图出现合法函数名字符但无对应声明 |
| `BoundaryError` | Agent 越界（不反弹 / 不穿墙 / 不环绕） |
| `MaxTicksExceeded` | （调试限制，非语言语义） |

---

## 项目结构

```text
XFeng/
├─ doc.md                  # 语言规范
├─ README.md
├─ LICENSE                 # MIT
├─ pyproject.toml          # 打包配置（pip install -e . 后可装出 xfeng / htmlc 命令）
├─ Makefile                # make test / make ide / make html / make clean
├─ compile.py              # 一键生成网页 IDE（等价 python -m htmlc）
├─ xfeng/                  # 解释器包
│  ├─ errors.py            # 错误分类
│  ├─ parser.py            # 解析与校验
│  ├─ interpreter.py       # 执行引擎（State / step / run）
│  ├─ cli.py               # 命令行入口
│  └─ __main__.py
├─ htmlc/                  # HTML 编译器包
│  ├─ compiler.py          # 编译逻辑
│  ├─ template.html        # 网页 IDE 模板（内嵌 JS 解析器 + 解释器 + 编辑器）
│  └─ __main__.py
├─ examples/               # 示例程序（*.xfeng）
├─ tests/                  # 单元测试
└─ .github/workflows/      # GitHub Actions CI（跑测试 + 冒烟编译）
```

## License

MIT License · © 2026 XFeng contributors

