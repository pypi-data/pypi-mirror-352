#!/usr/bin/env python3
"""
Grafana Loki 直接部署方案安装配置
支持pip install -e .进行本地开发安装
支持发布到PyPI供用户直接安装
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# 获取项目根目录
HERE = Path(__file__).parent.absolute()

# 读取README文件作为长描述
def read_file(file_path: str) -> str:
    """读取文件内容"""
    try:
        with open(HERE / file_path, encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

# 读取requirements.txt中的依赖
def read_requirements(file_path: str) -> list:
    """读取requirements文件并解析依赖"""
    requirements = []
    try:
        with open(HERE / file_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if line and not line.startswith('#'):
                    # 移除注释部分
                    if '#' in line:
                        line = line.split('#')[0].strip()
                    requirements.append(line)
    except FileNotFoundError:
        pass
    return requirements

# 获取版本号
def get_version():
    """从代码中获取版本号"""
    version_file = HERE / "grafana_loki_push" / "__init__.py"
    if version_file.exists():
        # 读取版本号
        with open(version_file, encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    
    return "1.0.0"  # 默认版本

# 分离运行时依赖和开发依赖
def parse_requirements():
    """解析requirements.txt，分离运行时和开发依赖"""
    # 运行时依赖（核心功能必需）
    install_requires = [
        'requests>=2.31.0',
        'loguru>=0.7.2',
        'pyyaml>=6.0.1',
        'click>=8.1.7',
        'python-json-logger>=2.0.7',
    ]
    
    # 开发依赖
    dev_requirements = [
        'pytest>=7.4.4',
        'pytest-cov>=4.1.0',
        'black>=23.12.1',
        'flake8>=6.1.0',
        'mypy>=1.8.0',
    ]
    
    # 构建依赖
    build_requirements = [
        'setuptools>=69.0.3',
        'wheel>=0.42.0',
        'build>=1.0.0',
        'twine>=4.0.0',
    ]
    
    return install_requires, dev_requirements, build_requirements

# 解析依赖
install_requires, dev_requirements, build_requirements = parse_requirements()

# 项目元数据
PACKAGE_NAME = "grafana-loki-push"
DESCRIPTION = "一键部署 Grafana Loki 系统，支持 HTTP 直接推送日志，无需 Promtail"
LONG_DESCRIPTION = read_file("README.md")
AUTHOR = "SeanZou"
AUTHOR_EMAIL = "wersling@gmail.com"
URL = "https://github.com/wersling/grafana-loki-push"
VERSION = get_version()

# 分类器
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Logging",
    "Topic :: System :: Monitoring",
    "Topic :: System :: Systems Administration",
]

# 关键词
KEYWORDS = [
    "grafana", "loki", "logging", "loguru", "observability", 
    "monitoring", "logs", "docker", "http-push", "prometheus"
]

if __name__ == "__main__":
    setup(
        # 基本信息
        name=PACKAGE_NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        
        # 作者信息
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        
        # 项目分类
        classifiers=CLASSIFIERS,
        keywords=KEYWORDS,
        license="MIT",
        
        # Python版本要求
        python_requires=">=3.8",
        
        # 包配置
        packages=find_packages(where="."),
        
        # 包含非Python文件
        include_package_data=True,
        package_data={
            'grafana_loki_push': [
                'docker-compose.yml',
                'config/*.yml',
                'config/*.yaml',
                'config/*.json',
                'config/*.conf'
            ]
        },
        
        # 依赖配置
        install_requires=install_requires,
        extras_require={
            "dev": dev_requirements,
            "build": build_requirements,
            "all": dev_requirements + build_requirements,
        },
        
        # 命令行工具
        entry_points={
            "console_scripts": [
                "loki-deploy=grafana_loki_push.cli:main",  # 修正入口点
                "grafana-loki=grafana_loki_push.cli:main",  # 修正入口点
            ],
        },
        
        # 项目URLs
        project_urls={
            "Documentation": f"{URL}#readme",
            "Source": URL,
            "Tracker": f"{URL}/issues",
            "Changelog": f"{URL}/releases",
        },
        
        # 其他配置
        zip_safe=False,  # 不压缩安装，便于调试
        platforms=["any"],
    ) 