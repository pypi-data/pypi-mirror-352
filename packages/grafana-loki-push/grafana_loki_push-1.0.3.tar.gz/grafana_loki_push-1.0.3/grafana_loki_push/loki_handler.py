"""
Loki Handler for Loguru
用于loguru的Loki日志处理器，支持通过logger.add()直接接入
"""

import json
import time
import threading
import queue
import sys
import traceback
import atexit
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from loguru import logger as loguru_logger
from .loki_client import LokiHTTPClient, LogStream, LogEntry


class LokiHandler:
    """
    Loguru兼容的Loki处理器
    
    使用方法:
        from grafana_loki_push.loki_handler import LokiHandler
        from loguru import logger
        
        # 简单使用（自动退出时发送）
        logger.add(LokiHandler(), format="{message}")
        
        # 自定义配置
        handler = LokiHandler(
            loki_url="http://localhost:3100",
            service="my-app",
            environment="production",
            batch_size=10,
            flush_interval=5.0,
            auto_flush_on_exit=True  # 程序退出时自动发送剩余日志
        )
        logger.add(handler, format="{time} {level} {message}")
    """
    
    # 类级别的处理器列表，用于自动清理
    _instances = []
    _atexit_registered = False
    
    def __init__(self, 
                 loki_url: str = "http://localhost:3100",
                 service: str = "default",
                 environment: str = "development",
                 extra_labels: Optional[Dict[str, str]] = None,
                 batch_size: int = 10,
                 flush_interval: float = 5.0,
                 max_queue_size: int = 1000,
                 debug: bool = False,
                 auto_flush_on_exit: bool = True):
        """
        初始化Loki处理器
        
        Args:
            loki_url: Loki服务地址
            service: 服务名称
            environment: 环境名称
            extra_labels: 额外的标签
            batch_size: 批量发送大小
            flush_interval: 发送间隔（秒）
            max_queue_size: 最大队列大小
            debug: 是否开启调试模式
            auto_flush_on_exit: 程序退出时是否自动发送剩余日志
        """
        self.loki_client = LokiHTTPClient(loki_url)
        self.service = service
        self.environment = environment
        self.extra_labels = extra_labels or {}
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.max_queue_size = max_queue_size
        self.debug = debug
        self.auto_flush_on_exit = auto_flush_on_exit
        
        # 日志队列和批量处理
        self.log_queue = queue.Queue(maxsize=max_queue_size)
        self.batch_logs: List[Dict[str, Any]] = []
        self.last_flush_time = time.time()
        
        # 后台线程处理
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()
        
        # 注册到类实例列表（用于自动清理）
        if self.auto_flush_on_exit:
            LokiHandler._instances.append(self)
            self._register_atexit()
        
        # 简单输出初始化信息（避免使用loguru）
        if self.debug:
            print(f"[LOKI] Loki Handler初始化完成: {loki_url}, 服务: {service}", file=sys.stderr)
            if self.auto_flush_on_exit:
                print("[LOKI] 已启用程序退出时自动发送剩余日志", file=sys.stderr)
    
    @classmethod
    def _register_atexit(cls):
        """注册程序退出时的清理函数"""
        if not cls._atexit_registered:
            atexit.register(cls._cleanup_all_instances)
            cls._atexit_registered = True
    
    @classmethod
    def _cleanup_all_instances(cls):
        """清理所有实例"""
        if cls._instances:
            print("[LOKI] 程序退出，正在发送剩余日志...", file=sys.stderr)
            for handler in cls._instances[:]:  # 复制列表避免修改时出错
                try:
                    handler._final_flush()
                except Exception as e:
                    print(f"[LOKI] 清理实例时出错: {e}", file=sys.stderr)
            cls._instances.clear()
    
    def _final_flush(self):
        """最终刷新，确保所有日志都发送"""
        # 停止工作线程
        self._stop_event.set()
        
        # 处理队列中剩余的日志
        remaining_logs = []
        try:
            while True:
                log_data = self.log_queue.get_nowait()
                remaining_logs.append(log_data)
        except queue.Empty:
            pass
        
        # 合并批量日志和剩余日志
        all_logs = self.batch_logs + remaining_logs
        if all_logs:
            if self.debug:
                print(f"[LOKI] 最终发送 {len(all_logs)} 条日志", file=sys.stderr)
            
            # 临时设置batch_logs用于发送
            self.batch_logs = all_logs
            self._flush_logs()
        
        # 等待工作线程结束
        if self._worker_thread.is_alive():
            self._worker_thread.join(timeout=3)
        
        # 从实例列表中移除
        if self in LokiHandler._instances:
            LokiHandler._instances.remove(self)
    
    def __call__(self, message) -> None:
        """
        loguru处理器接口
        可以接收格式化后的字符串或loguru的record对象
        
        Args:
            message: 格式化后的日志消息字符串或loguru的record对象
        """
        try:
            if isinstance(message, str):
                # 处理格式化后的字符串
                log_data = self._parse_formatted_message(message)
            else:
                # 处理loguru的record对象（更准确）
                log_data = self._extract_log_data(message)
            
            # 添加到队列
            if not self.log_queue.full():
                self.log_queue.put_nowait(log_data)
            else:
                # 队列满了，直接丢弃（避免阻塞）
                if self.debug:
                    print("[LOKI] 日志队列已满，丢弃日志", file=sys.stderr)
                
        except Exception as e:
            # 避免日志处理错误影响主程序
            if self.debug:
                print(f"[LOKI] Handler处理日志失败: {e}", file=sys.stderr)
    
    def _parse_formatted_message(self, message: str) -> Dict[str, Any]:
        """
        解析格式化的日志消息，尝试提取级别信息
        支持常见的日志格式模式
        """
        import re
        
        # 常见的日志级别关键词
        level_patterns = [
            (r'\[?(TRACE|trace)\]?', 'trace'),
            (r'\[?(DEBUG|debug)\]?', 'debug'),
            (r'\[?(INFO|info)\]?', 'info'),
            (r'\[?(SUCCESS|success)\]?', 'success'),
            (r'\[?(WARNING|warning|WARN|warn)\]?', 'warning'),
            (r'\[?(ERROR|error|ERR|err)\]?', 'error'),
            (r'\[?(CRITICAL|critical|CRIT|crit|FATAL|fatal)\]?', 'critical'),
        ]
        
        detected_level = "info"  # 默认级别
        clean_message = message
        
        # 调试输出
        if self.debug:
            print(f"[LOKI] 解析消息: '{message}'", file=sys.stderr)
        
        # 尝试从消息中检测级别
        for pattern, level in level_patterns:
            if re.search(pattern, message):
                detected_level = level
                if self.debug:
                    print(f"[LOKI] 检测到级别: {level} (匹配模式: {pattern})", file=sys.stderr)
                break
        
        if self.debug:
            print(f"[LOKI] 最终级别: {detected_level}", file=sys.stderr)
        
        return {
            "timestamp": int(time.time() * 1_000_000_000),
            "level": detected_level,
            "message": message,  # 保持原始消息
            "extra": {},
            "file": "",
            "function": "",
            "line": "",
            "process": "",
            "thread": ""
        }
    
    def write(self, message: str) -> None:
        """
        实现write方法，使其可以作为类似文件的对象使用
        这样可以更好地与loguru集成
        """
        # 移除可能的换行符
        message = message.rstrip('\n\r')
        if message:  # 只处理非空消息
            self.__call__(message)
    
    def _extract_log_data(self, record: Any) -> Dict[str, Any]:
        """提取loguru日志记录中的数据"""
        try:
            # 处理时间戳
            if hasattr(record, 'get') and 'time' in record:
                # record是dict-like对象
                time_obj = record.get("time")
                if hasattr(time_obj, 'timestamp'):
                    timestamp = int(time_obj.timestamp() * 1_000_000_000)
                else:
                    timestamp = int(time.time() * 1_000_000_000)
            else:
                timestamp = int(time.time() * 1_000_000_000)
            
            # 处理日志级别
            level = "info"
            if hasattr(record, 'get') and 'level' in record:
                level_obj = record.get("level")
                if hasattr(level_obj, 'name'):
                    level = level_obj.name.lower()
                elif isinstance(level_obj, str):
                    level = level_obj.lower()
            
            # 处理消息
            message = ""
            if hasattr(record, 'get') and 'message' in record:
                message = str(record.get("message", ""))
            elif isinstance(record, str):
                message = record
            
            # 处理额外信息
            extra = {}
            if hasattr(record, 'get') and 'extra' in record:
                extra = record.get("extra", {})
            
            # 处理文件信息
            file_info = ""
            function_info = ""
            line_info = ""
            
            if hasattr(record, 'get'):
                file_obj = record.get("file", {})
                if hasattr(file_obj, 'name'):
                    file_info = file_obj.name
                elif isinstance(file_obj, str):
                    file_info = file_obj
                
                function_info = str(record.get("function", ""))
                line_info = str(record.get("line", ""))
            
            return {
                "timestamp": timestamp,
                "level": level,
                "message": message,
                "extra": extra,
                "file": file_info,
                "function": function_info,
                "line": line_info,
                "process": "",
                "thread": ""
            }
            
        except Exception as e:
            # 如果解析失败，返回基本数据
            if self.debug:
                print(f"[LOKI] 解析record失败: {e}", file=sys.stderr)
            
            return {
                "timestamp": int(time.time() * 1_000_000_000),
                "level": "info",
                "message": str(record),
                "extra": {},
                "file": "",
                "function": "",
                "line": "",
                "process": "",
                "thread": ""
            }
    
    def _worker(self):
        """后台工作线程，处理日志发送"""
        while not self._stop_event.is_set():
            try:
                # 等待日志到达
                try:
                    # 阻塞等待第一条日志（超时1秒检查停止信号）
                    log_data = self.log_queue.get(timeout=1.0)
                    self.batch_logs.append(log_data)
                except queue.Empty:
                    # 超时，但如果有积累的日志需要检查时间触发
                    if self.batch_logs:
                        current_time = time.time()
                        if current_time - self.last_flush_time >= self.flush_interval:
                            self._flush_logs()
                    continue
                
                # 立即尝试获取更多日志，不等待
                while len(self.batch_logs) < self.batch_size:
                    try:
                        # 非阻塞获取更多日志
                        log_data = self.log_queue.get_nowait()
                        self.batch_logs.append(log_data)
                    except queue.Empty:
                        # 队列为空，给一个短暂的机会让更多日志进入
                        time.sleep(0.01)  # 10ms
                        # 再次尝试
                        try:
                            log_data = self.log_queue.get_nowait()
                            self.batch_logs.append(log_data)
                        except queue.Empty:
                            # 确实没有更多日志了
                            break
                
                # 检查发送条件
                current_time = time.time()
                should_flush = (
                    len(self.batch_logs) >= self.batch_size or
                    (self.batch_logs and current_time - self.last_flush_time >= self.flush_interval)
                )
                
                if should_flush:
                    self._flush_logs()
                    
            except Exception as e:
                if self.debug:
                    print(f"[LOKI] 工作线程错误: {e}", file=sys.stderr)
                time.sleep(1)  # 避免错误循环
    
    def _flush_logs(self):
        """发送批量日志到Loki"""
        if not self.batch_logs:
            return
        
        try:
            # 按标签分组日志
            grouped_logs = self._group_logs_by_labels()
            
            # 转换为Loki格式并发送
            streams = []
            for labels, logs in grouped_logs.items():
                entries = []
                for log_data in logs:
                    entry = LogEntry(
                        timestamp=log_data["timestamp"],
                        message=self._format_log_message(log_data)
                    )
                    entries.append(entry)
                
                stream = LogStream(labels=dict(labels), entries=entries)
                streams.append(stream)
            
            # 发送到Loki（禁用客户端内部的调试日志）
            if streams:
                # 临时禁用客户端调试
                old_debug = getattr(self.loki_client, 'debug', False)
                self.loki_client.debug = False
                
                success = self.loki_client.push_logs(streams)
                
                # 恢复客户端调试设置
                self.loki_client.debug = old_debug
                
                if self.debug:
                    if success:
                        print(f"[LOKI] 成功发送 {len(self.batch_logs)} 条日志到Loki", file=sys.stderr)
                    else:
                        print(f"[LOKI] 发送 {len(self.batch_logs)} 条日志到Loki失败", file=sys.stderr)
            
        except Exception as e:
            if self.debug:
                print(f"[LOKI] 发送日志到Loki时发生错误: {e}", file=sys.stderr)
        finally:
            # 清空批量日志
            self.batch_logs.clear()
            self.last_flush_time = time.time()
    
    def _group_logs_by_labels(self) -> Dict[tuple, List[Dict[str, Any]]]:
        """按标签分组日志"""
        grouped = {}
        
        if self.debug:
            print(f"[LOKI] 开始分组 {len(self.batch_logs)} 条日志", file=sys.stderr)
        
        for log_data in self.batch_logs:
            # 构建基础标签
            labels = {
                "service": self.service,
                "environment": self.environment,
                "level": log_data["level"],
                "job": "loguru-handler"
            }
            
            if self.debug:
                print(f"[LOKI] 日志: level={log_data['level']}, message='{log_data['message'][:50]}...'", file=sys.stderr)
            
            # 添加文件信息标签
            if log_data["file"]:
                labels["file"] = log_data["file"]
            if log_data["function"]:
                labels["function"] = log_data["function"]
            
            # 添加额外标签
            labels.update(self.extra_labels)
            
            # 从extra中添加标签（如果有loki_labels）
            extra = log_data.get("extra", {})
            if "loki_labels" in extra and isinstance(extra["loki_labels"], dict):
                labels.update(extra["loki_labels"])
            
            # 使用元组作为key（因为dict不能作为key）
            labels_tuple = tuple(sorted(labels.items()))
            
            if labels_tuple not in grouped:
                grouped[labels_tuple] = []
            grouped[labels_tuple].append(log_data)
        
        if self.debug:
            print(f"[LOKI] 分组结果: {len(grouped)} 个不同的标签组", file=sys.stderr)
            for labels_tuple, logs in grouped.items():
                labels_dict = dict(labels_tuple)
                print(f"[LOKI] 组: {labels_dict['level']} - {len(logs)} 条日志", file=sys.stderr)
        
        return grouped
    
    def _format_log_message(self, log_data: Dict[str, Any]) -> str:
        """格式化日志消息"""
        message = log_data["message"]
        
        # 添加结构化信息
        structured_data = {}
        
        # 添加位置信息
        if log_data["file"] or log_data["function"] or log_data["line"]:
            structured_data["location"] = {
                "file": log_data["file"],
                "function": log_data["function"],
                "line": log_data["line"]
            }
        
        # 添加进程/线程信息
        if log_data["process"] or log_data["thread"]:
            structured_data["runtime"] = {
                "process": log_data["process"],
                "thread": log_data["thread"]
            }
        
        # 添加extra数据（排除loki_labels）
        extra = log_data.get("extra", {})
        filtered_extra = {k: v for k, v in extra.items() if k != "loki_labels"}
        if filtered_extra:
            structured_data["extra"] = filtered_extra
        
        # 如果有结构化数据，创建JSON格式
        if structured_data:
            full_data = {
                "message": message,
                "timestamp": datetime.fromtimestamp(log_data["timestamp"] / 1_000_000_000).isoformat(),
                "level": log_data["level"].upper(),
                **structured_data
            }
            return json.dumps(full_data, ensure_ascii=False, default=str)
        else:
            # 简单消息格式
            dt = datetime.fromtimestamp(log_data["timestamp"] / 1_000_000_000)
            return f"[{dt.strftime('%Y-%m-%d %H:%M:%S')}] [{log_data['level'].upper()}] {message}"
    
    def flush(self):
        """立即发送所有缓存的日志"""
        if self.batch_logs:
            self._flush_logs()
    
    def close(self):
        """关闭处理器"""
        # 如果启用了auto_flush_on_exit，执行最终刷新
        if self.auto_flush_on_exit:
            self._final_flush()
        else:
            # 停止工作线程
            self._stop_event.set()
            
            # 发送剩余日志
            self.flush()
            
            # 等待工作线程结束
            if self._worker_thread.is_alive():
                self._worker_thread.join(timeout=5)
        
        # 关闭Loki客户端
        self.loki_client.close()
        
        if self.debug:
            print("[LOKI] Loki Handler已关闭", file=sys.stderr)
    
    def __del__(self):
        """析构函数，确保资源清理"""
        try:
            self.close()
        except:
            pass


# 便捷函数
def add_loki_handler(loki_url: str = "http://localhost:3100",
                     service: str = "default",
                     environment: str = "development",
                     level: str = "INFO",
                     format_string: str = "{message}",
                     debug: bool = False,
                     auto_flush_on_exit: bool = True,
                     **kwargs) -> int:
    """
    便捷函数：添加Loki处理器到loguru
    
    Args:
        loki_url: Loki服务地址
        service: 服务名称
        environment: 环境名称
        level: 日志级别
        format_string: 日志格式
        debug: 是否开启调试模式
        auto_flush_on_exit: 程序退出时是否自动发送剩余日志
        **kwargs: 传递给LokiHandler的其他参数
    
    Returns:
        int: handler的ID，可用于后续移除
    """
    handler = LokiHandler(
        loki_url=loki_url,
        service=service,
        environment=environment,
        debug=debug,
        auto_flush_on_exit=auto_flush_on_exit,
        **kwargs
    )
    
    handler_id = loguru_logger.add(
        handler.write,  # 使用write方法
        level=level,
        format=format_string,
        backtrace=True,
        diagnose=True
    )
    
    return handler_id


def remove_loki_handler(handler_id: int):
    """
    移除Loki处理器
    
    Args:
        handler_id: add_loki_handler返回的ID
    """
    loguru_logger.remove(handler_id) 