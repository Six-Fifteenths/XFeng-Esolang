# XFeng 1.0 — 常用任务
# Windows 下请把 `python3` 换成 `python`

PY ?= python3

.PHONY: test check ide html dist clean

## 运行全部单元测试
test:
	$(PY) -m unittest discover -s tests -v

## 只校验程序（不执行）
check:
	$(PY) -m xfeng examples/fib.xfeng --check

## 生成通用网页 IDE（内置示例）
ide:
	$(PY) -m htmlc -o ide.html

## 把 examples/ 下所有 .xfeng 生成为预加载的 IDE 页（dist/*.html）
html dist:
	@mkdir -p dist
	@for f in examples/*.xfeng; do \
		$(PY) -m htmlc "$$f" -o "dist/$$(basename "$$f" .xfeng).html"; \
	done

## 清理生成物与缓存
clean:
	rm -rf dist ide.html
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
