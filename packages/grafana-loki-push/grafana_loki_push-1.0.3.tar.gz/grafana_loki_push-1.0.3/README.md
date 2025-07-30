# 🚀 Grafana Loki Push - Python 日志处理器

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/grafana-loki-push.svg)](https://pypi.org/project/grafana-loki-push/)

🔥 **核心特性**：无需 Promtail，直接通过 HTTP 推送日志到 Loki！完美集成 loguru，支持程序退出时自动发送剩余日志。

## ✨ 主要特性

### 🎯 一键集成 loguru
- **一行代码**集成现有项目日志系统
- 支持所有 loguru 日志级别和格式化
- 自动提取日志字段和标签

### 🔄 HTTP 直接推送
- 无需 Promtail 中间件，直接推送到 Loki
- 支持批量推送，高性能日志处理
- 自动重试机制，确保日志不丢失

### 📦 **程序退出自动发送**
- **关键特性**：程序退出时自动发送缓存中的剩余日志
- 支持正常退出、异常退出、信号中断
- 确保所有日志都能成功推送到 Loki

### 🛠️ 完整工具链
- 命令行工具：`loki-deploy`
- 支持日志平台一键部署
- 包含 Grafana 可视化界面

## 🚀 快速开始

### 安装

```bash
# 直接通过 pip 安装
pip install grafana-loki-push
```

### 基础使用

```python
from grafana_loki_push import add_loki_handler
from loguru import logger

# 一行代码启用 Loki 日志，支持自动退出发送！
add_loki_handler(
    service="my-app", 
    environment="production",
    auto_flush_on_exit=True  # 关键特性！
)

# 正常使用 loguru
logger.info("应用启动")
logger.warning("这是一条警告")
logger.error("发生错误")

# 程序退出时自动发送剩余日志到 Loki
```

### 部署 Loki 平台

```bash
# 一键部署 Loki + Grafana（需要 Docker）
loki-deploy deploy

# 访问 Grafana: http://localhost:3000 (admin/admin123)
```

## 📖 详细使用指南

### 🎯 方式一：便捷函数（推荐）

```python
from grafana_loki_push import add_loki_handler, remove_loki_handler
from loguru import logger

# 一行代码添加 Loki 输出
handler_id = add_loki_handler(
    service="my-app",
    environment="production",
    auto_flush_on_exit=True
)

# 正常使用 loguru
logger.info("Hello Loki!")
logger.warning("这是一条警告")
logger.error("这是一条错误")

# 移除handler（可选）
remove_loki_handler(handler_id)
```

### 🔧 方式二：直接使用 LokiHandler

```python
from grafana_loki_push import LokiHandler
from loguru import logger

# 创建 handler
handler = LokiHandler(
    loki_url="http://localhost:3100",
    service="my-service",
    environment="production",
    auto_flush_on_exit=True
)

# 添加到 loguru
handler_id = logger.add(handler, format="{message}")

# 使用完成后清理
logger.remove(handler_id)
handler.close()
```

## ⚙️ 高级配置

### 完整配置参数

```python
from grafana_loki_push import LokiHandler

handler = LokiHandler(
    # 基础配置
    loki_url="http://localhost:3100",    # Loki 服务地址
    service="my-service",                # 服务名称
    environment="production",            # 环境标识
    
    # 性能配置
    batch_size=20,                       # 批量发送大小
    flush_interval=3.0,                  # 发送间隔（秒）
    max_queue_size=1000,                 # 最大队列大小
    
    # 功能配置
    auto_flush_on_exit=True,             # 自动退出发送 ⭐
    debug=False,                         # 调试模式
    
    # 网络配置
    timeout=30,                          # 请求超时（秒）
    retry_attempts=3,                    # 重试次数
    
    # 自定义标签
    extra_labels={                       # 额外的固定标签
        "version": "1.0.0",
        "region": "us-west-1"
    }
)
```

### 配置参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `loki_url` | str | `http://localhost:3100` | Loki 服务地址 |
| `service` | str | `default` | 服务名称，用作标签 |
| `environment` | str | `development` | 环境名称（dev/test/prod） |
| `batch_size` | int | `10` | 批量发送的日志条数 |
| `flush_interval` | float | `5.0` | 自动发送间隔（秒） |
| `max_queue_size` | int | `1000` | 内存队列最大大小 |
| `auto_flush_on_exit` | bool | `False` | **程序退出时自动发送** ⭐ |
| `debug` | bool | `False` | 是否开启调试输出 |
| `timeout` | int | `30` | HTTP 请求超时时间 |
| `retry_attempts` | int | `3` | 失败重试次数 |
| `extra_labels` | dict | `{}` | 额外的固定标签 |

## 🔄 自动退出发送详解

这是本项目的核心特性，确保程序退出时不丢失日志。

### 启用自动退出发送

```python
from grafana_loki_push import add_loki_handler
from loguru import logger

# 启用自动退出发送
add_loki_handler(
    service="my-app",
    auto_flush_on_exit=True  # 关键参数！
)

logger.info("程序开始执行")
logger.info("处理重要数据...")

# 程序在这里可能会因为异常退出
# 但前面的日志依然会被发送到 Loki
```

### 支持的退出情况

- ✅ **正常退出**：程序正常结束
- ✅ **异常退出**：未捕获的异常导致程序崩溃
- ✅ **信号中断**：SIGTERM、SIGINT（Ctrl+C）
- ✅ **系统关闭**：Docker 容器停止、系统重启

### 手动触发发送

```python
# 手动发送缓存的日志
handler.flush()

# 或者关闭时自动发送
handler.close()
```

## 📊 结构化日志

### 基础结构化日志

```python
from loguru import logger

# 使用 extra 参数传递结构化数据
logger.info("用户登录", extra={
    "user_id": "12345",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "session_id": "sess_abc123"
})
```

### 自定义 Loki 标签

```python
# 使用 loki_labels 指定哪些字段作为 Loki 标签
logger.info("API 请求", extra={
    "endpoint": "/api/users",       # 这个会在消息体中
    "response_time": 120,           # 这个也在消息体中
    "loki_labels": {                # 这些会成为 Loki 标签
        "method": "GET",
        "status_code": "200",
        "api_version": "v1"
    }
})
```

### 使用 bind 创建上下文 logger

```python
# 为特定模块创建专用 logger
auth_logger = logger.bind(loki_labels={"module": "auth"})
auth_logger.info("用户登录成功")
auth_logger.error("登录失败")

# 为特定用户会话创建 logger
session_logger = logger.bind(
    session_id="sess_123",
    loki_labels={"module": "user_session"}
)
session_logger.info("用户进入首页")
session_logger.info("用户查看商品")
```

## 🛠️ 命令行工具

安装后可在任何目录使用：

```bash
# 服务管理
loki-deploy deploy          # 部署 Loki + Grafana
loki-deploy stop           # 停止服务  
loki-deploy restart        # 重启服务
loki-deploy status         # 查看状态

# 日志管理
loki-deploy logs           # 查看服务日志
loki-deploy example        # 运行示例
loki-deploy test           # 测试连接

# 工具功能
loki-deploy push "消息"    # 推送单条日志

# 帮助信息
loki-deploy --help
grafana-loki --help        # 备用命令
```

详细的部署和运维指南请参考：[grafana-loki-push.md](grafana-loki-push.md)

## 💡 最佳实践

### 1. 生产环境配置

```python
# 生产环境推荐配置
add_loki_handler(
    service="my-production-app",
    environment="production",
    batch_size=50,                # 增大批量大小
    flush_interval=2.0,           # 缩短发送间隔
    auto_flush_on_exit=True,      # 必须启用
    extra_labels={
        "version": "1.2.3",
        "datacenter": "us-east-1"
    }
)
```

### 2. 开发环境配置

```python
# 开发环境配置
add_loki_handler(
    service="my-dev-app",
    environment="development",
    debug=True,                   # 开启调试输出
    flush_interval=1.0,           # 更频繁的发送
    auto_flush_on_exit=True
)
```

### 3. 结构化日志规范

```python
# 推荐的日志结构
logger.info("业务操作", extra={
    # 业务数据（会在日志内容中）
    "business_data": {...},
    "metrics": {...},
    
    # Loki 标签（用于查询过滤）
    "loki_labels": {
        "operation": "user_registration",
        "module": "user_service",
        "status": "success"
    }
})
```

## 🔧 故障排除

### 常见问题

1. **连接不上 Loki**
   ```python
   # 检查 Loki 是否运行
   loki-deploy status
   
   # 测试连接
   loki-deploy test
   ```

2. **日志发送失败**
   ```python
   # 开启调试模式查看详细信息
   add_loki_handler(debug=True)
   ```

3. **程序退出时日志丢失**
   ```python
   # 确保启用自动退出发送
   add_loki_handler(auto_flush_on_exit=True)
   
   # 或手动发送
   handler.flush()
   ```

### 日志级别映射

| loguru 级别 | Loki 标签 |
|------------|----------|
| TRACE      | trace    |
| DEBUG      | debug    |
| INFO       | info     |
| SUCCESS    | info     |
| WARNING    | warning  |
| ERROR      | error    |
| CRITICAL   | critical |

## 📦 项目结构

```
grafana-loki-push/
├── 📦 核心包
│   └── grafana_loki_push/
│       ├── __init__.py          # 包初始化和API导出
│       ├── loki_handler.py      # Loguru处理器（核心）
│       ├── loki_client.py       # HTTP客户端
│       ├── loki_deployment.py   # 部署管理
│       └── cli.py               # 命令行工具
│
├── 🎯 配置文件
│   ├── config/                  # Loki和Grafana配置
│   ├── docker-compose.yml       # Docker编排
│   ├── setup.py                 # 安装配置
│   └── requirements.txt         # 依赖管理
│
└── 📚 文档
    ├── README.md                # 本文档（Handler使用指南）
    └── grafana-loki-push.md     # 部署和运维指南
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。

---

⭐ 如果这个项目对你有帮助，请给个 Star！

🔗 **相关文档**：
- [部署和运维指南](grafana-loki-push.md) - 详细的 Loki 平台部署说明
- [PyPI 页面](https://pypi.org/project/grafana-loki-push/) - 包发布信息 