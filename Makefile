# XFeng 1.0 — 常用任务
# Windows 下请把 `python3` 换成 `python`

PY ?= python3

.PHONY: test check clean

## 运行全部单元测试
test:
	$(PY) -m unittest discover -s tests -v

## 只校验程序（不执行）
check:
	$(PY) -m xfeng examples/fib.xfeng --check

## 清理本地生成物与缓存
clean:
	rm -rf dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
