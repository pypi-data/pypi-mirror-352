#!/usr/bin/env python3
"""
安装验证测试
验证pip install -e .后的功能是否正常
"""

import sys
import traceback
from loguru import logger

def test_package_import():
    """测试包导入"""
    print("🔍 测试包导入...")
    try:
        import grafana_loki_push
        print(f"   ✅ grafana_loki_push包导入成功")
        print(f"   📦 版本: {grafana_loki_push.get_version()}")
        
        # 测试具体组件导入
        from grafana_loki_push import LokiHandler, LokiHTTPClient, LokiDeployment
        print(f"   ✅ 核心类导入成功: LokiHandler, LokiHTTPClient, LokiDeployment")
        
        from grafana_loki_push import add_loki_handler, remove_loki_handler
        print(f"   ✅ 便捷函数导入成功: add_loki_handler, remove_loki_handler")
        
        return True
    except Exception as e:
        print(f"   ❌ 包导入失败: {e}")
        traceback.print_exc()
        return False

def test_loki_handler():
    """测试LokiHandler基本功能"""
    print("\n🔧 测试LokiHandler...")
    try:
        from grafana_loki_push import LokiHandler
        
        # 创建handler（不连接到真实服务）
        handler = LokiHandler(
            loki_url="http://fake-url:3100",  # 假URL，不会真实连接
            service="test-install",
            environment="testing",
            debug=False,
            auto_flush_on_exit=True,
            batch_size=5,
            flush_interval=10.0  # 长间隔避免真实发送
        )
        
        print(f"   ✅ LokiHandler创建成功")
        print(f"   📊 服务: {handler.service}")
        print(f"   🌍 环境: {handler.environment}")
        print(f"   🔄 auto_flush_on_exit: {handler.auto_flush_on_exit}")
        
        # 测试close方法
        handler.close()
        print(f"   ✅ handler.close()成功")
        
        return True
    except Exception as e:
        print(f"   ❌ LokiHandler测试失败: {e}")
        traceback.print_exc()
        return False

def test_loguru_integration():
    """测试与loguru的集成"""
    print("\n📝 测试loguru集成...")
    try:
        from grafana_loki_push import LokiHandler
        
        # 移除默认handler避免混乱
        logger.remove()
        logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}")
        
        # 创建handler（不会真实发送）
        handler = LokiHandler(
            loki_url="http://fake-url:3100",
            service="test-loguru",
            environment="testing",
            debug=False,
            auto_flush_on_exit=False,  # 避免自动发送
            batch_size=100,  # 大批量避免发送
            flush_interval=3600.0  # 长间隔避免发送
        )
        
        # 添加到loguru
        handler_id = logger.add(handler, format="{message}")
        print(f"   ✅ handler添加到loguru成功，ID: {handler_id}")
        
        # 发送测试日志（不会真实发送到服务器）
        logger.info("这是一条测试日志")
        logger.warning("这是一条警告日志")
        logger.error("这是一条错误日志")
        print(f"   ✅ 日志发送测试完成")
        
        # 清理
        logger.remove(handler_id)
        handler.close()
        print(f"   ✅ 清理完成")
        
        return True
    except Exception as e:
        print(f"   ❌ loguru集成测试失败: {e}")
        traceback.print_exc()
        return False

def test_convenience_function():
    """测试便捷函数"""
    print("\n🎯 测试便捷函数...")
    try:
        from grafana_loki_push import add_loki_handler, remove_loki_handler
        
        # 使用便捷函数添加handler（不会真实连接）
        handler_id = add_loki_handler(
            loki_url="http://fake-url:3100",
            service="test-convenience",
            environment="testing",
            debug=False,
            auto_flush_on_exit=False
        )
        print(f"   ✅ add_loki_handler成功，ID: {handler_id}")
        
        # 发送测试日志
        logger.info("使用便捷函数发送的测试日志")
        print(f"   ✅ 日志发送测试完成")
        
        # 移除handler
        remove_loki_handler(handler_id)
        print(f"   ✅ remove_loki_handler成功")
        
        return True
    except Exception as e:
        print(f"   ❌ 便捷函数测试失败: {e}")
        traceback.print_exc()
        return False

def test_package_info():
    """测试包信息"""
    print("\n📋 测试包信息...")
    try:
        import grafana_loki_push
        
        info = grafana_loki_push.get_info()
        print(f"   📦 包信息:")
        for key, value in info.items():
            print(f"      {key}: {value}")
        
        print(f"   ✅ 包信息获取成功")
        return True
    except Exception as e:
        print(f"   ❌ 包信息测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始安装验证测试")
    print("="*50)
    
    tests = [
        ("包导入", test_package_import),
        ("LokiHandler", test_loki_handler),
        ("loguru集成", test_loguru_integration),
        ("便捷函数", test_convenience_function),
        ("包信息", test_package_info),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试 {name} 出现未捕获异常: {e}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"🎯 测试结果汇总:")
    print(f"   ✅ 通过: {passed}")
    print(f"   ❌ 失败: {failed}")
    print(f"   📊 总计: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 所有测试通过！安装验证成功！")
        print("\n📋 下一步:")
        print("1. 运行 'loki-deploy deploy' 部署服务")
        print("2. 运行 'loki-deploy status' 检查状态") 
        print("3. 运行实际的日志测试")
        return True
    else:
        print("\n❌ 部分测试失败，请检查安装")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 