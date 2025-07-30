# Makefile - grafana-loki-push 项目管理

# 项目信息
PROJECT_NAME := grafana-loki-push

# Python和pip路径智能检测
# 优先使用虚拟环境中的 python 和 pip
PYTHON := $(shell which python 2>/dev/null || which python3 2>/dev/null || echo python3)
PIP := $(shell which pip 2>/dev/null || which pip3 2>/dev/null || echo pip3)

# 颜色定义
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# 目录定义
DIST_DIR := dist
BUILD_DIR := build
EGG_INFO_DIRS := $(wildcard *.egg-info)

# 环境检测
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    OS_TYPE := macos
else ifeq ($(UNAME_S),Linux)
    OS_TYPE := linux
else
    OS_TYPE := other
endif

.PHONY: help install install-dev test clean build publish test-publish docs lint format env-check env-setup

# 默认目标
help:
	@echo "$(BLUE)$(PROJECT_NAME) 项目管理命令$(RESET)"
	@echo ""
	@echo "$(GREEN)🚀 快速开始:$(RESET)"
	@echo "  env-check    - 检查Python环境"
	@echo "  env-setup    - 设置虚拟环境（推荐）"
	@echo "  setup        - 初始化开发环境"
	@echo "  release      - 一键测试发布到 TestPyPI"
	@echo "  publish      - 发布到正式 PyPI"
	@echo ""
	@echo "$(GREEN)📦 开发环境:$(RESET)"
	@echo "  install      - 安装项目依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  install-edit - 可编辑模式安装"
	@echo ""
	@echo "$(GREEN)🔧 代码质量:$(RESET)"
	@echo "  test         - 运行测试"
	@echo "  test-package - 测试已安装的包"
	@echo "  lint         - 代码检查"
	@echo "  format       - 代码格式化"
	@echo "  type-check   - 类型检查"
	@echo ""
	@echo "$(GREEN)🏗️  构建发布:$(RESET)"
	@echo "  clean        - 清理构建文件"
	@echo "  build        - 构建包"
	@echo "  check        - 检查包"
	@echo "  test-publish - 发布到测试PyPI"
	@echo ""
	@echo "$(GREEN)📚 文档:$(RESET)"
	@echo "  docs         - 生成文档"
	@echo "  docs-serve   - 启动文档服务"
	@echo ""
	@echo "$(GREEN)🔍 项目信息:$(RESET)"
	@echo "  info         - 显示项目信息"
	@echo "  version      - 显示版本信息"

# ==================== 环境检测和设置 ====================

env-check:
	@echo "$(BLUE)检查Python环境...$(RESET)"
	@echo "操作系统: $(OS_TYPE)"
	@echo "Python路径: $$(which $(PYTHON))"
	@echo "Python版本: $$($(PYTHON) --version)"
	@echo "pip路径: $$(which $(PIP))"
	@echo "pip版本: $$($(PIP) --version)"
	@if [ "$$VIRTUAL_ENV" != "" ]; then \
		echo "$(GREEN)✅ 当前在虚拟环境中: $$VIRTUAL_ENV$(RESET)"; \
	elif [ "$$CONDA_DEFAULT_ENV" != "" ]; then \
		echo "$(GREEN)✅ 当前在conda环境中: $$CONDA_DEFAULT_ENV$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️  当前使用系统Python，建议使用虚拟环境$(RESET)"; \
		echo "$(YELLOW)   运行 'make env-setup' 创建虚拟环境$(RESET)"; \
	fi

env-setup:
	@echo "$(BLUE)设置Python虚拟环境...$(RESET)"
	@if [ -d "venv" ]; then \
		echo "$(GREEN)虚拟环境已存在$(RESET)"; \
	else \
		echo "$(BLUE)创建虚拟环境...$(RESET)"; \
		$(PYTHON) -m venv venv; \
		echo "$(GREEN)✅ 虚拟环境创建完成$(RESET)"; \
	fi
	@echo ""
	@echo "$(YELLOW)请运行以下命令激活虚拟环境:$(RESET)"
	@if [ "$(OS_TYPE)" = "macos" ] || [ "$(OS_TYPE)" = "linux" ]; then \
		echo "  source venv/bin/activate"; \
	else \
		echo "  venv\\Scripts\\activate"; \
	fi
	@echo ""
	@echo "$(YELLOW)然后运行: make setup$(RESET)"

# ==================== 快速开始 ====================

setup: env-check install-build-deps install-edit
	@echo "$(GREEN)✅ 开发环境设置完成$(RESET)"
	@echo "$(YELLOW)现在可以运行: make release$(RESET)"

release: clean build check test-package test-publish
	@echo "$(GREEN)✅ 测试发布完成！$(RESET)"
	@echo "$(YELLOW)如果测试无问题，运行 'make publish' 发布到正式PyPI$(RESET)"

# ==================== 安装依赖 ====================

install:
	@echo "$(BLUE)安装项目依赖...$(RESET)"
	$(PIP) install -r requirements.txt

install-dev:
	@echo "$(BLUE)安装开发依赖...$(RESET)"
	$(PIP) install -e ".[dev]"

install-edit:
	@echo "$(BLUE)可编辑模式安装...$(RESET)"
	@if [ "$$VIRTUAL_ENV" != "" ]; then \
		echo "$(GREEN)使用虚拟环境安装...$(RESET)"; \
		$(PYTHON) -m pip install -e .; \
	elif [ "$$CONDA_DEFAULT_ENV" != "" ]; then \
		echo "$(GREEN)使用conda环境安装...$(RESET)"; \
		$(PYTHON) -m pip install -e .; \
	elif [ "$(OS_TYPE)" = "macos" ]; then \
		echo "$(YELLOW)Mac环境下使用用户安装...$(RESET)"; \
		$(PYTHON) -m pip install -e . --user --break-system-packages 2>/dev/null || \
		$(PYTHON) -m pip install -e . --user; \
	else \
		echo "$(YELLOW)使用用户安装...$(RESET)"; \
		$(PYTHON) -m pip install -e . --user; \
	fi

install-build-deps:
	@echo "$(BLUE)安装构建依赖...$(RESET)"
	@if [ "$$VIRTUAL_ENV" != "" ] || [ "$$CONDA_DEFAULT_ENV" != "" ]; then \
		$(PIP) install build twine setuptools wheel; \
	elif [ "$(OS_TYPE)" = "macos" ]; then \
		$(PIP) install build twine setuptools wheel --user --break-system-packages 2>/dev/null || \
		$(PIP) install build twine setuptools wheel --user; \
	else \
		$(PIP) install build twine setuptools wheel --user; \
	fi

# ==================== 代码质量检查 ====================

test:
	@echo "$(BLUE)运行测试...$(RESET)"
	@if [ -d "tests" ]; then \
		$(PYTHON) -m pytest tests/ -v --cov=grafana_loki_push --cov-report=html; \
	else \
		echo "$(YELLOW)⚠️  没有找到tests目录，跳过测试$(RESET)"; \
	fi

test-package:
	@echo "$(BLUE)测试已安装的包...$(RESET)"
	@$(PYTHON) -c "import grafana_loki_push; print('✅ 导入成功，版本:', grafana_loki_push.__version__)"
	@$(PYTHON) -c "from grafana_loki_push import LokiHandler, LokiHTTPClient, add_loki_handler; print('✅ 核心组件导入成功')"
	@loki-deploy --help > /dev/null && echo "✅ 命令行工具可用" || echo "❌ 命令行工具不可用"
	@echo "$(GREEN)✅ 包测试完成$(RESET)"

lint:
	@echo "$(BLUE)代码检查...$(RESET)"
	@if command -v flake8 >/dev/null 2>&1; then \
		$(PYTHON) -m flake8 grafana_loki_push/ --max-line-length=88 --extend-ignore=E203,W503; \
		echo "$(GREEN)✅ 代码检查通过$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️  flake8 未安装，跳过代码检查$(RESET)"; \
	fi

format:
	@echo "$(BLUE)格式化代码...$(RESET)"
	@if command -v black >/dev/null 2>&1; then \
		$(PYTHON) -m black grafana_loki_push/ --line-length 88; \
		echo "$(GREEN)✅ 代码格式化完成$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️  black 未安装，跳过代码格式化$(RESET)"; \
	fi

type-check:
	@echo "$(BLUE)类型检查...$(RESET)"
	@if command -v mypy >/dev/null 2>&1; then \
		$(PYTHON) -m mypy grafana_loki_push/ --ignore-missing-imports; \
		echo "$(GREEN)✅ 类型检查通过$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️  mypy 未安装，跳过类型检查$(RESET)"; \
	fi

# ==================== 构建和发布 ====================

clean:
	@echo "$(BLUE)清理构建文件...$(RESET)"
	@rm -rf $(DIST_DIR) $(BUILD_DIR) $(EGG_INFO_DIRS)
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ 清理完成$(RESET)"

build: clean
	@echo "$(BLUE)构建包...$(RESET)"
	@$(PYTHON) -m build
	@echo "$(GREEN)✅ 构建完成$(RESET)"
	@echo "$(BLUE)📦 构建产物:$(RESET)"
	@ls -la $(DIST_DIR)/

check: 
	@echo "$(BLUE)检查包...$(RESET)"
	@if [ ! -d "$(DIST_DIR)" ] || [ -z "$$(ls -A $(DIST_DIR) 2>/dev/null)" ]; then \
		echo "$(YELLOW)⚠️  未找到构建产物，先构建包...$(RESET)"; \
		$(MAKE) build; \
	fi
	@$(PYTHON) -m twine check $(DIST_DIR)/*
	@echo "$(GREEN)✅ 包检查通过$(RESET)"

test-publish: check
	@echo "$(YELLOW)🚀 发布到测试PyPI...$(RESET)"
	@echo "$(YELLOW)请确保已配置 TestPyPI 凭据$(RESET)"
	@$(PYTHON) -m twine upload --repository testpypi $(DIST_DIR)/*
	@echo "$(GREEN)✅ 发布到测试PyPI成功!$(RESET)"
	@echo "$(BLUE)📦 测试安装命令:$(RESET)"
	@$(PYTHON) -c "import grafana_loki_push; print('pip install --index-url https://test.pypi.org/simple/ grafana-loki-push==' + grafana_loki_push.__version__)"

publish: check
	@echo "$(RED)🚀 发布到正式PyPI...$(RESET)"
	@$(PYTHON) -c "import grafana_loki_push; version = grafana_loki_push.__version__; print(f'即将发布版本 {version} 到正式PyPI')"
	@read -p "确认发布吗? (yes/no): " answer && [ "$$answer" = "yes" ]
	@$(PYTHON) -m twine upload $(DIST_DIR)/*
	@echo "$(GREEN)✅ 发布到PyPI成功!$(RESET)"
	@echo "$(BLUE)📦 安装命令:$(RESET)"
	@$(PYTHON) -c "import grafana_loki_push; print('pip install grafana-loki-push==' + grafana_loki_push.__version__)"

# ==================== 文档相关 ====================

docs:
	@echo "$(BLUE)生成文档...$(RESET)"
	@echo "$(YELLOW)TODO: 添加文档生成命令$(RESET)"

docs-serve:
	@echo "$(BLUE)启动文档服务...$(RESET)"
	@echo "$(YELLOW)TODO: 添加文档服务命令$(RESET)"

# ==================== 项目信息 ====================

info:
	@echo "$(BLUE)项目信息:$(RESET)"
	@echo "  名称: $(PROJECT_NAME)"
	@echo "  Python版本: $$($(PYTHON) --version)"
	@echo "  项目路径: $$(pwd)"
	@echo "  虚拟环境: $(VIRTUAL_ENV)"

version:
	@echo "$(BLUE)版本信息:$(RESET)"
	@$(PYTHON) -c "import grafana_loki_push; print(f'当前版本: {grafana_loki_push.__version__}')"

# ==================== 开发流程快捷方式 ====================

dev-setup: install-dev
	@echo "$(GREEN)✅ 开发环境设置完成$(RESET)"

dev-check: format lint type-check test-package
	@echo "$(GREEN)✅ 代码质量检查完成$(RESET)"

dev-build: clean build check
	@echo "$(GREEN)✅ 构建完成$(RESET)" 