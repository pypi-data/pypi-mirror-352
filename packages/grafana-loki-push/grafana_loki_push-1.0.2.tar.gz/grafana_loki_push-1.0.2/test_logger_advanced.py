"""
高级Loki Handler测试文件
测试各种功能包括结构化日志、错误处理等
"""

import time
import sys
from loguru import logger
from grafana_loki_push.loki_handler import LokiHandler, add_loki_handler


def test_basic_functionality():
    """测试基础功能"""
    print("=== 测试1: 基础功能 ===")
    
    # 移除默认handler
    logger.remove()
    
    # 添加控制台输出便于观察
    logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}")
    
    # 添加Loki handler（开启调试模式）
    logger.add(LokiHandler(debug=True), format="{message}")
    
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.debug("这是一条调试日志")
    
    time.sleep(3)
    print("基础功能测试完成\n")


def test_structured_logging():
    """测试结构化日志"""
    print("=== 测试2: 结构化日志 ===")
    
    # 使用便捷函数
    handler_id = add_loki_handler(
        service="test-app",
        environment="development",
        debug=True,
        extra_labels={"version": "1.0.0"}
    )
    
    # 带额外数据的日志
    logger.info("用户登录", extra={
        "user_id": "12345",
        "ip": "192.168.1.100",
        "browser": "Chrome"
    })
    
    # 带Loki标签的日志
    logger.error("支付失败", extra={
        "order_id": "order_123",
        "amount": 99.99,
        "loki_labels": {
            "payment_method": "credit_card",
            "error_category": "timeout"
        }
    })
    
    # 使用bind创建上下文logger
    context_logger = logger.bind(
        session_id="sess_abc123",
        loki_labels={"module": "checkout"}
    )
    
    context_logger.info("开始结账流程")
    context_logger.warning("库存不足")
    context_logger.info("结账完成")
    
    time.sleep(3)
    logger.remove(handler_id)
    print("结构化日志测试完成\n")


def test_error_handling():
    """测试错误处理"""
    print("=== 测试3: 错误处理 ===")
    
    add_loki_handler(service="error-test", debug=True)
    
    try:
        # 故意制造一个异常
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.exception("除零错误发生", extra={
            "operation": "division",
            "numerator": 10,
            "denominator": 0,
            "loki_labels": {"error_type": "math_error"}
        })
    
    try:
        # 另一个异常
        data = {"key": "value"}
        value = data["nonexistent_key"]
    except KeyError as e:
        logger.exception("键错误", extra={
            "missing_key": "nonexistent_key",
            "available_keys": list(data.keys()),
            "loki_labels": {"error_type": "key_error"}
        })
    
    time.sleep(3)
    print("错误处理测试完成\n")


def test_performance():
    """测试性能 - 大量日志"""
    print("=== 测试4: 性能测试 ===")
    
    # 配置较大的批量大小
    handler = LokiHandler(
        service="perf-test",
        batch_size=50,
        flush_interval=2.0,
        debug=True
    )
    logger.add(handler, format="{message}")
    
    # 快速生成大量日志
    start_time = time.time()
    for i in range(100):
        logger.info(f"性能测试日志 {i+1}/100", extra={
            "iteration": i+1,
            "batch": i // 10,
            "loki_labels": {"test_type": "performance"}
        })
    
    end_time = time.time()
    logger.info(f"生成100条日志耗时: {end_time - start_time:.2f}秒")
    
    # 等待所有日志发送完成
    time.sleep(5)
    handler.flush()  # 强制发送剩余日志
    
    print("性能测试完成\n")


def test_different_formats():
    """测试不同格式"""
    print("=== 测试5: 不同格式测试 ===")
    
    # 移除之前的handlers
    logger.remove()
    logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}")
    
    # 测试不同的格式字符串
    formats = [
        "{message}",
        "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        "[{time:HH:mm:ss}] {level.name:8} | {name}:{function}:{line} - {message}"
    ]
    
    for i, format_str in enumerate(formats):
        print(f"测试格式 {i+1}: {format_str}")
        
        handler_id = add_loki_handler(
            service=f"format-test-{i+1}",
            format_string=format_str,
            debug=True
        )
        
        logger.info(f"使用格式{i+1}的测试消息")
        logger.warning(f"格式{i+1}的警告消息")
        
        time.sleep(2)
        logger.remove(handler_id)
    
    print("格式测试完成\n")


def main():
    """主测试函数"""
    print("开始运行Loki Handler高级测试...\n")
    
    try:
        test_basic_functionality()
        test_structured_logging()
        test_error_handling()
        test_performance()
        test_different_formats()
        
        print("🎉 所有测试完成！")
        print("\n现在可以在Grafana中查看这些日志:")
        print("1. 访问 http://localhost:3000")
        print("2. 使用 admin/admin123 登录")
        print("3. 进入 Explore 页面")
        print("4. 查询示例:")
        print("   - {service=\"test-app\"}")
        print("   - {error_category=\"timeout\"}")
        print("   - {test_type=\"performance\"}")
        print("   - {module=\"checkout\"}")
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 等待最后的日志发送
        print("\n等待日志发送完成...")
        time.sleep(3)


if __name__ == "__main__":
    main() 