"""
Grafana Loki 直接部署方案

一键部署完整的 Grafana Loki 系统，支持 HTTP 直接推送日志，无需 Promtail！

主要特性:
- 🎯 一键部署：Docker Compose 自动化部署 Loki + Grafana
- 🔄 HTTP 直推：无需 Promtail，直接通过 HTTP API 推送日志
- 📊 可视化：预配置 Grafana 数据源，开箱即用
- 🔧 loguru 集成：一行代码接入现有项目日志系统
- 📦 批量处理：高性能批量日志推送，支持自定义标签
- 🛠️ CLI 工具：完整的命令行管理工具

使用示例:
    # 简单使用
    from grafana_loki_push import add_loki_handler
    from loguru import logger
    
    add_loki_handler(service="my-app")
    logger.info("Hello Loki!")
    
    # 自定义配置
    from grafana_loki_push import LokiHandler
    
    handler = LokiHandler(
        service="my-service",
        environment="production",
        auto_flush_on_exit=True
    )
    logger.add(handler, format="{message}")
"""

__version__ = "4"
__author__ = "SeanZou"
__email__ = "wersling@gmail.com"
__license__ = "MIT"

# 主要导入，方便用户使用
try:
    from .loki_handler import LokiHandler, add_loki_handler, remove_loki_handler
    from .loki_client import LokiHTTPClient, LogStream, LogEntry
    from .loki_deployment import LokiDeployment
    
    # 导出的公共API
    __all__ = [
        # 版本信息
        "__version__",
        "__author__", 
        "__email__",
        "__license__",
        
        # 核心类
        "LokiHandler",
        "LokiHTTPClient", 
        "LokiDeployment",
        
        # 便捷函数
        "add_loki_handler",
        "remove_loki_handler",
        
        # 数据类
        "LogStream",
        "LogEntry",
    ]
    
except ImportError as e:
    # 如果导入失败，只导出版本信息
    import warnings
    warnings.warn(f"部分模块导入失败: {e}，请检查依赖是否正确安装", ImportWarning)
    
    __all__ = [
        "__version__",
        "__author__", 
        "__email__",
        "__license__",
    ]


def get_version():
    """获取当前版本号"""
    return __version__


def get_info():
    """获取包信息"""
    return {
        "name": "grafana-loki-push",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "description": "一键部署 Grafana Loki 系统，支持 HTTP 直接推送日志"
    }


def main():
    """命令行入口点"""
    from .cli import main as cli_main
    cli_main() 