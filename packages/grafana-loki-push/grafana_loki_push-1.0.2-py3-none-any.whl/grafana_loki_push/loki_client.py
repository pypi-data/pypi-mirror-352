"""
Loki HTTP客户端
用于直接向Loki发送日志数据，不依赖Promtail
"""

import json
import requests
import time
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LogEntry:
    """日志条目数据类"""
    timestamp: int  # 纳秒级时间戳
    message: str    # 日志消息内容
    
    
@dataclass 
class LogStream:
    """日志流数据类"""
    labels: Dict[str, str]  # 标签键值对
    entries: List[LogEntry] # 日志条目列表


class LokiHTTPClient:
    """Loki HTTP客户端，用于向Loki发送日志"""
    
    def __init__(self, loki_url: str = "http://localhost:3100", timeout: int = 30, debug: bool = False):
        """
        初始化Loki客户端
        
        Args:
            loki_url: Loki服务的URL地址
            timeout: 请求超时时间（秒）
            debug: 是否开启调试模式
        """
        self.loki_url = loki_url.rstrip('/')
        self.push_url = f"{self.loki_url}/loki/api/v1/push"
        self.timeout = timeout
        self.debug = debug
        self.session = requests.Session()
        
        # 设置默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'LokiHTTPClient/1.0'
        })
        
        if self.debug:
            print(f"[LOKI] Loki客户端初始化完成，服务器地址: {self.loki_url}", file=sys.stderr)
    
    def _get_timestamp_ns(self) -> int:
        """获取当前纳秒级时间戳"""
        return int(time.time() * 1_000_000_000)
    
    def _format_timestamp(self, timestamp: Optional[int] = None) -> str:
        """格式化时间戳为Loki要求的字符串格式"""
        if timestamp is None:
            timestamp = self._get_timestamp_ns()
        return str(timestamp)
    
    def push_log(self, 
                 message: str, 
                 labels: Dict[str, str],
                 timestamp: Optional[int] = None) -> bool:
        """
        推送单条日志到Loki
        
        Args:
            message: 日志消息内容
            labels: 日志标签
            timestamp: 时间戳（纳秒），如果为None则使用当前时间
            
        Returns:
            bool: 推送是否成功
        """
        if timestamp is None:
            timestamp = self._get_timestamp_ns()
            
        log_entry = LogEntry(timestamp=timestamp, message=message)
        log_stream = LogStream(labels=labels, entries=[log_entry])
        
        return self.push_logs([log_stream])
    
    def push_logs(self, streams: List[LogStream]) -> bool:
        """
        批量推送日志流到Loki
        
        Args:
            streams: 日志流列表
            
        Returns:
            bool: 推送是否成功
        """
        try:
            # 构造Loki API格式的payload
            payload = {
                "streams": []
            }
            
            for stream in streams:
                stream_data = {
                    "stream": stream.labels,
                    "values": []
                }
                
                for entry in stream.entries:
                    # Loki期望的格式: [timestamp_string, message]
                    stream_data["values"].append([
                        self._format_timestamp(entry.timestamp),
                        entry.message
                    ])
                
                payload["streams"].append(stream_data)
            
            if self.debug:
                print(f"[LOKI] 准备推送日志到Loki: {json.dumps(payload, indent=2)}", file=sys.stderr)
            
            # 发送HTTP POST请求
            response = self.session.post(
                self.push_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 204:
                if self.debug:
                    print(f"[LOKI] 成功推送 {len(streams)} 个日志流到Loki", file=sys.stderr)
                return True
            else:
                if self.debug:
                    print(f"[LOKI] 推送日志失败: HTTP {response.status_code}, {response.text}", file=sys.stderr)
                return False
                
        except requests.exceptions.RequestException as e:
            if self.debug:
                print(f"[LOKI] 网络请求失败: {e}", file=sys.stderr)
            return False
        except Exception as e:
            if self.debug:
                print(f"[LOKI] 推送日志时发生未知错误: {e}", file=sys.stderr)
            return False
    
    def push_log_with_level(self,
                           message: str,
                           level: str = "info",
                           service: str = "unknown",
                           extra_labels: Optional[Dict[str, str]] = None) -> bool:
        """
        推送带有日志级别的日志
        
        Args:
            message: 日志消息
            level: 日志级别 (debug, info, warn, error)
            service: 服务名称
            extra_labels: 额外的标签
            
        Returns:
            bool: 推送是否成功
        """
        labels = {
            "level": level,
            "service": service,
            "job": "http-push"
        }
        
        if extra_labels:
            labels.update(extra_labels)
            
        return self.push_log(message, labels)
    
    def test_connection(self) -> bool:
        """
        测试与Loki的连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 尝试访问Loki的health端点
            health_url = f"{self.loki_url}/ready"
            response = self.session.get(health_url, timeout=5)
            
            if response.status_code == 200:
                if self.debug:
                    print("[LOKI] Loki连接测试成功", file=sys.stderr)
                return True
            else:
                if self.debug:
                    print(f"[LOKI] Loki连接测试失败: HTTP {response.status_code}", file=sys.stderr)
                return False
                
        except Exception as e:
            if self.debug:
                print(f"[LOKI] Loki连接测试异常: {e}", file=sys.stderr)
            return False
    
    def close(self):
        """关闭HTTP会话"""
        self.session.close()
        if self.debug:
            print("[LOKI] Loki客户端会话已关闭", file=sys.stderr)


class LogFormatter:
    """日志格式化器"""
    
    @staticmethod
    def format_json_log(data: Dict[str, Any], 
                       timestamp: Optional[int] = None) -> LogEntry:
        """
        格式化JSON格式的日志
        
        Args:
            data: 要记录的数据
            timestamp: 时间戳
            
        Returns:
            LogEntry: 格式化后的日志条目
        """
        if timestamp is None:
            timestamp = int(time.time() * 1_000_000_000)
            
        message = json.dumps(data, ensure_ascii=False)
        return LogEntry(timestamp=timestamp, message=message)
    
    @staticmethod
    def format_text_log(message: str, 
                       level: str = "info",
                       timestamp: Optional[int] = None) -> LogEntry:
        """
        格式化文本格式的日志
        
        Args:
            message: 日志消息
            level: 日志级别
            timestamp: 时间戳
            
        Returns:
            LogEntry: 格式化后的日志条目
        """
        if timestamp is None:
            timestamp = int(time.time() * 1_000_000_000)
            
        # 添加时间戳和级别信息到消息中
        dt = datetime.fromtimestamp(timestamp / 1_000_000_000)
        formatted_message = f"[{dt.strftime('%Y-%m-%d %H:%M:%S')}] [{level.upper()}] {message}"
        
        return LogEntry(timestamp=timestamp, message=formatted_message) 