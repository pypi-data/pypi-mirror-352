#!/usr/bin/env python3
"""
Grafana Loki HTTP Push 命令行接口
提供命令行工具来管理Loki服务的部署和日志推送功能
"""

import sys
import argparse
from pathlib import Path
from loguru import logger

# 导入本包的模块
try:
    # 尝试相对导入（在包内使用时）
    from .loki_deployment import LokiDeployment
    from .loki_client import LokiHTTPClient
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from grafana_loki_push.loki_deployment import LokiDeployment
    from grafana_loki_push.loki_client import LokiHTTPClient


def setup_logger():
    """配置日志记录器"""
    logger.remove()  # 移除默认处理器
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )


def deploy_command(args):
    """部署Loki服务"""
    deployment = LokiDeployment()
    
    logger.info("开始部署Grafana Loki服务...")
    
    success = deployment.deploy(detached=not args.foreground)
    
    if success:
        logger.success("Loki服务部署成功!")
        
        # 显示服务访问地址
        urls = deployment.get_service_urls()
        logger.info("服务访问地址:")
        logger.info(f"  Grafana Web界面: {urls['grafana']}")
        logger.info(f"  Loki API地址: {urls['loki']}")
        logger.info(f"  日志推送API: {urls['loki_push_api']}")
        logger.info(f"  Grafana登录: {urls['grafana_login']}")
        
        logger.info("\n可以运行以下命令测试日志推送:")
        logger.info("loki-deploy example")
    else:
        logger.error("Loki服务部署失败")
        sys.exit(1)


def stop_command(args):
    """停止Loki服务"""
    deployment = LokiDeployment()
    
    logger.info("正在停止Loki服务...")
    
    success = deployment.stop()
    
    if success:
        logger.success("Loki服务已停止")
    else:
        logger.error("停止Loki服务失败")
        sys.exit(1)


def restart_command(args):
    """重启Loki服务"""
    deployment = LokiDeployment()
    
    logger.info("正在重启Loki服务...")
    
    success = deployment.restart()
    
    if success:
        logger.success("Loki服务重启成功")
        
        # 显示服务访问地址
        urls = deployment.get_service_urls()
        logger.info("服务访问地址:")
        logger.info(f"  Grafana Web界面: {urls['grafana']}")
        logger.info(f"  Loki API地址: {urls['loki']}")
    else:
        logger.error("Loki服务重启失败")
        sys.exit(1)


def status_command(args):
    """查看服务状态"""
    deployment = LokiDeployment()
    
    logger.info("检查Loki服务状态...")
    
    status_info = deployment.get_status()
    
    if "error" in status_info:
        logger.error(f"获取状态信息失败: {status_info['error']}")
        sys.exit(1)
    
    # 显示Docker Compose状态
    logger.info("Docker Compose服务状态:")
    print(status_info["docker_compose_output"])
    
    # 显示服务健康状态
    logger.info("服务健康检查:")
    if status_info["loki_healthy"]:
        logger.success("✓ Loki服务正常")
    else:
        logger.error("✗ Loki服务异常")
    
    if status_info["grafana_healthy"]:
        logger.success("✓ Grafana服务正常")
    else:
        logger.error("✗ Grafana服务异常")
    
    # 显示日志统计信息
    if "total_logs_24h" in status_info:
        logger.info("📊 日志统计信息:")
        logger.info(f"  近24小时日志数量: {status_info['total_logs_24h']}")
        if "labels_count" in status_info:
            logger.info(f"  标签种类数量: {status_info['labels_count']}")
    
    # 显示访问地址
    logger.info("服务访问地址:")
    logger.info(f"  Grafana: {status_info['grafana_url']}")
    logger.info(f"  Loki: {status_info['loki_url']}")
    
    # 提示清空日志功能
    if status_info.get("total_logs_24h", 0) > 0:
        logger.info("💡 提示: 如需清空测试日志，运行 'loki-deploy clear'")


def logs_command(args):
    """查看服务日志"""
    deployment = LokiDeployment()
    
    logger.info(f"显示{'所有服务' if not args.service else args.service}日志...")
    
    success = deployment.show_logs(service=args.service, follow=args.follow)
    
    if not success:
        logger.error("显示日志失败")
        sys.exit(1)


def example_command(args):
    """运行日志推送示例"""
    logger.info("运行日志推送示例...")
    
    # 优先尝试使用独立的示例，如果不存在则使用内置示例
    try:
        # 先尝试导入examples模块
        from examples.log_push_example import LogPushExample
        
        example = LogPushExample()
        example.run_all_examples()
        logger.info("✅ 使用了完整的示例模块")
        
    except ImportError:
        # 如果示例模块不存在，使用简化的内置示例
        logger.info("📝 使用内置简化示例（examples模块未找到）")
        
        try:
            client = LokiHTTPClient("http://localhost:3100")
            
            # 测试连接
            if not client.test_connection():
                logger.error("无法连接到Loki服务，请先运行 'loki-deploy deploy'")
                sys.exit(1)
            
            logger.info("开始推送示例日志...")
            
            # 推送几条示例日志
            examples = [
                ("info", "应用启动成功", {"module": "startup"}),
                ("warning", "配置文件使用默认值", {"module": "config"}),
                ("error", "数据库连接失败", {"module": "database"}),
                ("info", "用户登录成功", {"module": "auth", "user_id": "12345"}),
            ]
            
            for level, message, extra_labels in examples:
                success = client.push_log_with_level(
                    message=message,
                    level=level,
                    service="cli-example",
                    labels=extra_labels
                )
                if success:
                    logger.info(f"✓ 推送{level}日志: {message}")
                else:
                    logger.error(f"✗ 推送{level}日志失败: {message}")
            
            logger.success("示例日志推送完成！")
            logger.info("你可以在Grafana中查看这些日志：http://localhost:3000")
            
            client.close()
            
        except Exception as e:
            logger.error(f"运行内置示例失败: {e}")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"运行示例失败: {e}")
        sys.exit(1)


def test_connection_command(args):
    """测试Loki连接"""
    client = LokiHTTPClient(args.loki_url)
    
    logger.info(f"测试连接到Loki服务: {args.loki_url}")
    
    if client.test_connection():
        logger.success("Loki连接测试成功")
        
        # 发送一条测试日志
        success = client.push_log_with_level(
            message="这是一条连接测试日志",
            level="info",
            service="connection-test"
        )
        
        if success:
            logger.success("测试日志推送成功")
        else:
            logger.error("测试日志推送失败")
    else:
        logger.error("Loki连接测试失败")
        sys.exit(1)
    
    client.close()


def push_log_command(args):
    """推送单条日志"""
    client = LokiHTTPClient(args.loki_url)
    
    logger.info(f"推送日志到Loki: {args.message}")
    
    success = client.push_log_with_level(
        message=args.message,
        level=args.level,
        service=args.service,
        labels=getattr(args, 'labels', {})
    )
    
    if success:
        logger.success("日志推送成功")
    else:
        logger.error("日志推送失败")
        sys.exit(1)
    
    client.close()


def clear_logs_command(args):
    """清空所有日志数据"""
    deployment = LokiDeployment()
    
    # 询问用户确认（除非使用--force参数）
    if not args.force:
        logger.warning("⚠️  即将清空所有日志数据，此操作不可恢复！")
        confirm = input("请输入 'yes' 确认删除所有日志: ")
        if confirm.lower() != 'yes':
            logger.info("操作已取消")
            return
    
    logger.info("开始清空日志数据...")
    
    success = deployment.clear_logs(confirm=True)
    
    if success:
        logger.success("✅ 所有日志数据已清空")
        logger.info("📊 现在可以重新开始记录日志")
    else:
        logger.error("❌ 清空日志数据失败")
        sys.exit(1)


def main():
    """主函数，处理命令行参数"""
    setup_logger()
    
    parser = argparse.ArgumentParser(
        description="Grafana Loki HTTP Push 部署管理器",
        epilog="""
示例命令:
  loki-deploy deploy              # 部署Loki服务
  loki-deploy deploy --foreground # 前台部署（显示详细日志）
  loki-deploy stop               # 停止服务
  loki-deploy restart            # 重启服务
  loki-deploy status             # 查看服务状态
  loki-deploy logs               # 查看所有服务日志
  loki-deploy logs --service loki --follow  # 跟踪Loki服务日志
  loki-deploy example            # 运行日志推送示例
  loki-deploy test               # 测试Loki连接
  loki-deploy clear              # 清空所有日志数据（需要确认）
  loki-deploy clear --force      # 强制清空（跳过确认）
  loki-deploy push "测试消息" --level info --service test-app
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 部署命令
    deploy_parser = subparsers.add_parser('deploy', help='部署Loki服务')
    deploy_parser.add_argument('--foreground', action='store_true', 
                             help='在前台运行，显示详细日志输出')
    deploy_parser.set_defaults(func=deploy_command)
    
    # 停止命令
    stop_parser = subparsers.add_parser('stop', help='停止Loki服务')
    stop_parser.set_defaults(func=stop_command)
    
    # 重启命令
    restart_parser = subparsers.add_parser('restart', help='重启Loki服务')
    restart_parser.set_defaults(func=restart_command)
    
    # 状态命令
    status_parser = subparsers.add_parser('status', help='查看服务状态')
    status_parser.set_defaults(func=status_command)
    
    # 日志命令
    logs_parser = subparsers.add_parser('logs', help='查看服务日志')
    logs_parser.add_argument('--service', choices=['loki', 'grafana'], 
                           help='指定查看特定服务的日志')
    logs_parser.add_argument('--follow', '-f', action='store_true',
                           help='持续跟踪日志输出')
    logs_parser.set_defaults(func=logs_command)
    
    # 示例命令
    example_parser = subparsers.add_parser('example', help='运行日志推送示例')
    example_parser.set_defaults(func=example_command)
    
    # 测试命令
    test_parser = subparsers.add_parser('test', help='测试Loki连接')
    test_parser.add_argument('--loki-url', default='http://localhost:3100',
                           help='Loki服务地址 (默认: http://localhost:3100)')
    test_parser.set_defaults(func=test_connection_command)
    
    # 清空日志命令
    clear_parser = subparsers.add_parser('clear', help='清空所有日志数据')
    clear_parser.add_argument('--force', action='store_true',
                            help='强制清空，跳过确认提示')
    clear_parser.set_defaults(func=clear_logs_command)
    
    # 推送日志命令
    push_parser = subparsers.add_parser('push', help='推送单条日志')
    push_parser.add_argument('message', help='日志消息内容')
    push_parser.add_argument('--level', default='info', 
                           choices=['debug', 'info', 'warning', 'error', 'critical'],
                           help='日志级别 (默认: info)')
    push_parser.add_argument('--service', default='cli-tool',
                           help='服务名称 (默认: cli-tool)')
    push_parser.add_argument('--loki-url', default='http://localhost:3100',
                           help='Loki服务地址 (默认: http://localhost:3100)')
    push_parser.set_defaults(func=push_log_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 执行对应的命令函数
    args.func(args)


if __name__ == "__main__":
    main() 