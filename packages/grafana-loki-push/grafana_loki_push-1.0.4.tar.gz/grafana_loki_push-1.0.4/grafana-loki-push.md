# 🚀 Grafana Loki 日志平台部署指南

> 完整的 Grafana Loki 服务部署、配置、管理和运维指南

## 📋 目录

- [快速部署](#快速部署)
- [环境要求](#环境要求)
- [命令行工具](#命令行工具)
- [服务配置](#服务配置)
- [数据查询](#数据查询)
- [运维监控](#运维监控)
- [故障排除](#故障排除)
- [生产部署](#生产部署)

## 🚀 快速部署

### 安装 grafana-loki-push

```bash
# 方法1：直接安装（推荐）
pip install grafana-loki-push

# 方法2：从源码安装
git clone https://github.com/wersling/grafana-loki-push.git
cd grafana-loki-push
pip install -e .
```

### 一键部署 Loki + Grafana

```bash
# 1. 部署服务
loki-deploy deploy

# 2. 验证部署
loki-deploy status

# 3. 测试日志推送
loki-deploy test

# 4. 运行示例
loki-deploy example
```

### 访问服务

部署成功后，可以访问以下服务：

- **Grafana**: http://localhost:3000
  - 用户名: `admin`
  - 密码: `admin123`
- **Loki API**: http://localhost:3100
  - 状态检查: http://localhost:3100/ready

## 🛠️ 环境要求

### 系统要求

- **操作系统**: Linux, macOS, Windows
- **Docker**: 20.10+
- **Docker Compose**: 1.29+
- **Python**: 3.8+
- **内存**: 最小 2GB，推荐 4GB+
- **磁盘**: 最小 10GB 可用空间

### 端口要求

确保以下端口可用：

| 服务 | 端口 | 说明 |
|------|------|------|
| Grafana | 3000 | Web UI |
| Loki | 3100 | HTTP API |

## 🛠️ 命令行工具详解

### 基础服务管理

```bash
# 部署服务
loki-deploy deploy              # 标准部署
loki-deploy deploy --foreground # 前台运行（查看详细输出）

# 服务控制
loki-deploy stop               # 停止所有服务
loki-deploy restart            # 重启所有服务
loki-deploy status             # 查看服务状态

# 服务日志
loki-deploy logs               # 查看所有服务日志
loki-deploy logs --service loki      # 查看 Loki 服务日志
loki-deploy logs --service grafana   # 查看 Grafana 服务日志
loki-deploy logs --follow      # 实时跟踪日志
```

### 数据管理

```bash
# 数据清理
loki-deploy clear              # 清空日志数据（需确认）
loki-deploy clear --force      # 强制清空日志数据

# 数据备份（手动）
docker cp loki_loki_1:/loki ./loki-backup
```

### 测试和调试

```bash
# 连接测试
loki-deploy test               # 测试本地 Loki 连接
loki-deploy test --loki-url http://remote:3100  # 测试远程 Loki

# 日志推送测试
loki-deploy push "测试消息"
loki-deploy push "错误信息" --level error --service my-app
loki-deploy push "远程日志" --loki-url http://remote:3100

# 运行示例
loki-deploy example            # 推送示例日志到 Loki
```

### 高级功能

```bash
# 查看详细帮助
loki-deploy --help
loki-deploy deploy --help

# 使用备用命令
grafana-loki --help           # 备用命令名
```

## ⚙️ 服务配置

### Docker Compose 配置

默认的 `docker-compose.yml` 配置：

```yaml
version: '3.8'

services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./config/loki-config.yml:/etc/loki/local-config.yaml
      - loki-data:/loki
    restart: unless-stopped
    networks:
      - loki-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - ./config/grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
      - grafana-data:/var/lib/grafana
    restart: unless-stopped
    networks:
      - loki-network
    depends_on:
      - loki

volumes:
  loki-data:
  grafana-data:

networks:
  loki-network:
    driver: bridge
```

### Loki 配置详解

`config/loki-config.yml` 主要配置：

```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  instance_addr: 127.0.0.1
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

limits_config:
  reject_old_samples: true
  reject_old_samples_max_age: 168h    # 7天
  ingestion_rate_mb: 16               # 每秒最大摄入16MB
  ingestion_burst_size_mb: 32         # 突发大小32MB
  per_stream_rate_limit: 512KB        # 每个流限制512KB/s
  per_stream_rate_limit_burst: 1024KB # 突发1MB

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: false
  retention_period: 0s

ruler:
  storage:
    type: local
    local:
      directory: /loki/rules
  rule_path: /loki/rules
  alertmanager_url: http://localhost:9093
  ring:
    kvstore:
      store: inmemory
  enable_api: true
```

### Grafana 数据源配置

`config/grafana-datasources.yml`：

```yaml
apiVersion: 1

datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: true
    editable: true
```

## 📊 数据查询

### LogQL 基础查询

```logql
# 查看所有日志
{job=~".+"}

# 按服务筛选
{service="my-app"}

# 按级别筛选
{service="my-app", level="error"}

# 按环境筛选
{environment="production"}

# 组合查询
{service="my-app", environment="production", level=~"error|critical"}
```

### 高级查询

```logql
# 时间范围过滤
{service="my-app"} |= "error" | json | line_format "{{.timestamp}} {{.message}}"

# 统计错误数量
sum(count_over_time({service="my-app", level="error"}[5m]))

# 按服务分组统计
sum by (service) (rate({job=~".+"}[5m]))

# 正则表达式过滤
{service="my-app"} |~ "user_id.*12345"
```

### 常用查询示例

```logql
# 1. 最近5分钟的错误日志
{level="error"} | json | line_format "{{.timestamp}} [{{.service}}] {{.message}}"

# 2. API 响应时间大于1秒的请求
{service="api"} | json | response_time > 1000

# 3. 特定用户的操作日志
{service="user-service"} | json | user_id="12345"

# 4. 按小时统计日志量
sum(count_over_time({job=~".+"}[1h])) by (service)

# 5. 错误率计算
sum(rate({level="error"}[5m])) / sum(rate({job=~".+"}[5m]))
```

## 🔍 运维监控

### 服务状态监控

```bash
# 检查服务状态
loki-deploy status

# 检查 Docker 容器
docker ps | grep -E "(loki|grafana)"

# 检查端口占用
netstat -tulpn | grep -E "(3000|3100)"
```

### 性能监控

```bash
# 查看资源使用情况
docker stats

# 查看磁盘使用
docker system df
du -sh $(docker volume inspect loki_loki-data -f '{{.Mountpoint}}')

# 查看网络连接
ss -tulpn | grep -E "(3000|3100)"
```

### 日志监控

```bash
# 实时查看 Loki 日志
loki-deploy logs --service loki --follow

# 查看 Grafana 日志
loki-deploy logs --service grafana --follow

# 查看错误日志
loki-deploy logs | grep -i error
```

### 健康检查

```bash
# Loki 健康检查
curl http://localhost:3100/ready
curl http://localhost:3100/metrics

# Grafana 健康检查
curl http://localhost:3000/api/health
```

## 🚨 故障排除

### 常见问题及解决方案

#### 1. 服务启动失败

```bash
# 检查端口冲突
sudo lsof -i :3000
sudo lsof -i :3100

# 检查 Docker 状态
docker --version
docker-compose --version

# 重新部署
loki-deploy stop
loki-deploy deploy
```

#### 2. 无法访问 Grafana

```bash
# 检查 Grafana 容器状态
docker ps | grep grafana

# 查看 Grafana 日志
loki-deploy logs --service grafana

# 重置 Grafana 密码
docker exec -it $(docker ps -q -f name=grafana) grafana-cli admin reset-admin-password admin123
```

#### 3. Loki 连接失败

```bash
# 测试 Loki 连接
loki-deploy test

# 检查 Loki 容器状态
docker ps | grep loki

# 查看 Loki 日志
loki-deploy logs --service loki
```

#### 4. 日志推送失败

```python
# 开启调试模式
from grafana_loki_push import add_loki_handler

add_loki_handler(
    service="debug-app",
    debug=True  # 开启调试输出
)
```

#### 5. 磁盘空间不足

```bash
# 清理 Docker 数据
docker system prune -f

# 清理 Loki 数据
loki-deploy clear

# 设置数据保留策略
# 编辑 config/loki-config.yml
# 添加 retention_period: 720h  # 30天
```

#### 6. 内存不足

```yaml
# 在 docker-compose.yml 中限制内存使用
services:
  loki:
    mem_limit: 1g
    memswap_limit: 1g
  grafana:
    mem_limit: 512m
    memswap_limit: 512m
```

### 调试技巧

```bash
# 1. 查看详细启动日志
loki-deploy deploy --foreground

# 2. 进入容器调试
docker exec -it $(docker ps -q -f name=loki) sh
docker exec -it $(docker ps -q -f name=grafana) bash

# 3. 查看配置文件
docker exec $(docker ps -q -f name=loki) cat /etc/loki/local-config.yaml

# 4. 手动测试 API
curl -H "Content-Type: application/json" -XPOST \
  "http://localhost:3100/loki/api/v1/push" \
  --data-raw '{"streams": [{"stream": {"job": "test"}, "values": [["'$(date +%s)000000000'", "test message"]]}]}'
```

## 🏭 生产部署

### 生产环境配置优化

#### 1. 性能优化配置

```yaml
# config/loki-config.yml 生产优化
limits_config:
  ingestion_rate_mb: 64           # 增加摄入速率
  ingestion_burst_size_mb: 128    # 增加突发大小
  max_query_parallelism: 32       # 增加查询并行度
  split_queries_by_interval: 15m  # 查询分割间隔

chunk_store_config:
  chunk_cache_config:
    enable_fifocache: true
    fifocache:
      max_size_items: 1024
  write_dedupe_cache_config:
    enable_fifocache: true
    fifocache:
      max_size_items: 1024
```

#### 2. 数据保留策略

```yaml
# 配置数据保留期
table_manager:
  retention_deletes_enabled: true
  retention_period: 2160h  # 90天
  
limits_config:
  retention_period: 2160h  # 90天
```

#### 3. 外部存储配置

```yaml
# 使用 S3 存储（生产推荐）
storage_config:
  aws:
    s3: s3://your-bucket-name/loki
    region: us-west-2
  boltdb_shipper:
    active_index_directory: /loki/index
    cache_location: /loki/cache
    shared_store: s3
```

### Docker Compose 生产配置

```yaml
version: '3.8'

services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./config/loki-config.yml:/etc/loki/local-config.yaml
      - loki-data:/loki
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    networks:
      - loki-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin123}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SECURITY_COOKIE_SECURE=true
      - GF_ANALYTICS_REPORTING_ENABLED=false
    volumes:
      - ./config/grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
      - grafana-data:/var/lib/grafana
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    networks:
      - loki-network
    depends_on:
      - loki
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  loki-data:
    driver: local
  grafana-data:
    driver: local

networks:
  loki-network:
    driver: bridge
```

### 安全配置

#### 1. 启用认证

```yaml
# config/loki-config.yml
auth_enabled: true

server:
  http_listen_port: 3100
  grpc_listen_port: 9096
  
# 添加认证配置
```

#### 2. 网络安全

```yaml
# docker-compose.yml 网络隔离
networks:
  loki-network:
    driver: bridge
    internal: true  # 内部网络，仅容器间通信

  web-network:
    driver: bridge  # 对外访问的网络
```

#### 3. 防火墙配置

```bash
# UFW 配置示例
sudo ufw allow 3000/tcp  # Grafana
sudo ufw allow 3100/tcp  # Loki (如需外部访问)
```

### 备份和恢复

#### 1. 数据备份

```bash
#!/bin/bash
# backup-loki.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/loki/$DATE"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份 Loki 数据
docker cp loki_loki_1:/loki $BACKUP_DIR/

# 备份 Grafana 数据
docker cp loki_grafana_1:/var/lib/grafana $BACKUP_DIR/

# 备份配置文件
cp -r config $BACKUP_DIR/
cp docker-compose.yml $BACKUP_DIR/

# 压缩备份
tar -czf "$BACKUP_DIR.tar.gz" -C /backup/loki $DATE

echo "备份完成: $BACKUP_DIR.tar.gz"
```

#### 2. 数据恢复

```bash
#!/bin/bash
# restore-loki.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "用法: $0 <backup_file.tar.gz>"
    exit 1
fi

# 停止服务
loki-deploy stop

# 解压备份
tar -xzf $BACKUP_FILE -C /tmp/

# 恢复数据
docker cp /tmp/*/loki/. loki_loki_1:/loki/
docker cp /tmp/*/grafana/. loki_grafana_1:/var/lib/grafana/

# 重启服务
loki-deploy restart

echo "恢复完成"
```

### 监控和告警

#### 1. Prometheus 监控

```yaml
# 添加 Prometheus 监控
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--web.enable-lifecycle'
```

#### 2. 告警配置

```yaml
# config/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'loki'
    static_configs:
      - targets: ['loki:3100']
  
  - job_name: 'grafana'
    static_configs:
      - targets: ['grafana:3000']
```

## 📚 相关资源

- **项目主页**: [GitHub Repository](https://github.com/wersling/grafana-loki-push)
- **Python 包**: [PyPI Package](https://pypi.org/project/grafana-loki-push/)
- **Loki Handler 使用指南**: [README.md](README.md)
- **官方文档**:
  - [Grafana Loki 文档](https://grafana.com/docs/loki/)
  - [LogQL 查询语言](https://grafana.com/docs/loki/latest/logql/)
  - [Grafana 文档](https://grafana.com/docs/grafana/)

## 🤝 支持

如果在部署过程中遇到问题：

1. **检查文档**: 先查阅本指南的故障排除部分
2. **运行诊断**: 使用 `loki-deploy status` 和 `loki-deploy test` 
3. **查看日志**: 使用 `loki-deploy logs` 查看详细日志
4. **提交 Issue**: [GitHub Issues](https://github.com/wersling/grafana-loki-push/issues)

---

📝 **文档更新**: 本指南会随着项目更新而持续改进，建议定期检查最新版本。 