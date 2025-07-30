"""
Loki部署管理器
用于管理Grafana Loki服务的部署、启动、停止和健康检查
"""

import os
import subprocess
import time
import requests
import shutil
from typing import Optional, Dict, Any
from pathlib import Path
from loguru import logger

try:
    # Python 3.9+
    from importlib import resources
except ImportError:
    # Python 3.7-3.8
    import importlib_resources as resources


class LokiDeployment:
    """Loki部署管理器"""
    
    def __init__(self, project_root: str = "."):
        """
        初始化部署管理器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root).absolute()
        self.docker_compose_file = self.project_root / "docker-compose.yml"
        self.config_dir = self.project_root / "config"
        self.loki_url = "http://localhost:3100"
        self.grafana_url = "http://localhost:3000"
        
        logger.info(f"Loki部署管理器初始化完成，项目路径: {self.project_root}")
    
    def _extract_config_files(self) -> bool:
        """
        从包内部提取配置文件到当前目录
        
        Returns:
            bool: 提取是否成功
        """
        try:
            # 如果配置文件已存在，询问是否覆盖
            if self.docker_compose_file.exists():
                logger.info(f"配置文件已存在: {self.docker_compose_file}")
                return True
            
            logger.info("从包中提取配置文件...")
            
            # 提取 docker-compose.yml
            try:
                with resources.files('grafana_loki_push').joinpath('docker-compose.yml').open('r', encoding='utf-8') as f:
                    docker_compose_content = f.read()
                
                with open(self.docker_compose_file, 'w', encoding='utf-8') as f:
                    f.write(docker_compose_content)
                logger.info(f"✅ 提取 docker-compose.yml 到: {self.docker_compose_file}")
                
            except Exception as e:
                logger.error(f"提取 docker-compose.yml 失败: {e}")
                return False
            
            # 创建配置目录
            self.config_dir.mkdir(exist_ok=True)
            
            # 提取配置文件
            config_files = [
                'loki-config.yml',
                'grafana-datasources.yml'
            ]
            
            for config_file in config_files:
                try:
                    with resources.files('grafana_loki_push.config').joinpath(config_file).open('r', encoding='utf-8') as f:
                        config_content = f.read()
                    
                    config_file_path = self.config_dir / config_file
                    with open(config_file_path, 'w', encoding='utf-8') as f:
                        f.write(config_content)
                    logger.info(f"✅ 提取 {config_file} 到: {config_file_path}")
                    
                except Exception as e:
                    logger.error(f"提取 {config_file} 失败: {e}")
                    return False
            
            logger.success("所有配置文件提取完成")
            return True
            
        except Exception as e:
            logger.error(f"提取配置文件时发生错误: {e}")
            return False
    
    def check_docker_compose(self) -> bool:
        """
        检查Docker Compose是否可用
        
        Returns:
            bool: Docker Compose是否可用
        """
        try:
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"Docker Compose可用: {result.stdout.strip()}")
                return True
            else:
                logger.error("Docker Compose不可用")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Docker Compose检查超时")
            return False
        except FileNotFoundError:
            logger.error("未找到docker-compose命令")
            return False
        except Exception as e:
            logger.error(f"检查Docker Compose时发生错误: {e}")
            return False
    
    def create_config_directory(self):
        """创建配置文件目录"""
        self.config_dir.mkdir(exist_ok=True)
        logger.info(f"配置目录已创建: {self.config_dir}")
    
    def deploy(self, detached: bool = True) -> bool:
        """
        部署Loki服务
        
        Args:
            detached: 是否以后台模式运行
            
        Returns:
            bool: 部署是否成功
        """
        try:
            # 检查Docker Compose可用性
            if not self.check_docker_compose():
                return False
            
            # 提取配置文件
            if not self._extract_config_files():
                logger.error("配置文件提取失败，无法继续部署")
                return False
            
            # 检查docker-compose.yml是否存在
            if not self.docker_compose_file.exists():
                logger.error(f"未找到docker-compose.yml文件: {self.docker_compose_file}")
                return False
            
            logger.info("开始部署Loki服务...")
            
            # 构建docker-compose命令
            cmd = ["docker-compose", "-f", str(self.docker_compose_file), "up"]
            if detached:
                cmd.append("-d")
            
            # 切换到项目目录
            old_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )
                
                if result.returncode == 0:
                    logger.success("Loki服务部署成功")
                    logger.info(f"部署输出: {result.stdout}")
                    
                    if detached:
                        # 等待服务启动
                        logger.info("等待服务启动...")
                        time.sleep(30)  # 增加等待时间到30秒
                        
                        # 检查服务健康状态（带重试）
                        if self._check_health_with_retry():
                            logger.success("所有服务已成功启动并运行正常")
                            return True
                        else:
                            logger.warning("服务部署完成但健康检查失败")
                            return False
                    
                    return True
                else:
                    logger.error(f"部署失败: {result.stderr}")
                    return False
                    
            finally:
                os.chdir(old_cwd)
                
        except subprocess.TimeoutExpired:
            logger.error("部署超时")
            return False
        except Exception as e:
            logger.error(f"部署过程中发生错误: {e}")
            return False
    
    def stop(self) -> bool:
        """
        停止Loki服务
        
        Returns:
            bool: 停止是否成功
        """
        try:
            logger.info("正在停止Loki服务...")
            
            # 切换到项目目录
            old_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            try:
                result = subprocess.run(
                    ["docker-compose", "-f", str(self.docker_compose_file), "down"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    logger.success("Loki服务已停止")
                    return True
                else:
                    logger.error(f"停止服务失败: {result.stderr}")
                    return False
                    
            finally:
                os.chdir(old_cwd)
                
        except Exception as e:
            logger.error(f"停止服务时发生错误: {e}")
            return False
    
    def restart(self) -> bool:
        """
        重启Loki服务
        
        Returns:
            bool: 重启是否成功
        """
        logger.info("正在重启Loki服务...")
        
        if self.stop():
            time.sleep(5)  # 等待服务完全停止
            return self.deploy()
        else:
            return False
    
    def clear_logs(self, confirm: bool = False) -> bool:
        """
        清空Loki中的所有日志数据
        
        Args:
            confirm: 是否确认清空操作（安全措施）
            
        Returns:
            bool: 清空操作是否成功
        """
        if not confirm:
            logger.warning("清空日志操作需要确认。请在调用时设置 confirm=True")
            logger.warning("⚠️  注意：此操作将永久删除所有日志数据，无法恢复！")
            return False
        
        try:
            logger.warning("🗑️  开始清空Loki日志数据...")
            logger.warning("⚠️  此操作将删除所有历史日志，无法恢复！")
            
            # 第一步：停止服务
            logger.info("1️⃣  停止Loki服务...")
            if not self.stop():
                logger.error("停止服务失败，清空操作中止")
                return False
            
            # 等待服务完全停止
            time.sleep(5)
            
            # 第二步：删除Docker volumes（数据存储）
            logger.info("2️⃣  删除Loki数据卷...")
            if not self._remove_data_volumes():
                logger.warning("删除数据卷时遇到问题，但继续执行")
            
            # 第三步：清理本地数据目录（如果有）
            logger.info("3️⃣  清理本地数据目录...")
            self._clean_local_data()
            
            # 第四步：重新启动服务（使用重试机制）
            logger.info("4️⃣  重新启动服务...")
            if self._deploy_with_retry():
                logger.success("✅ Loki日志数据已成功清空，服务已重新启动")
                return True
            else:
                logger.error("重新启动服务失败")
                return False
                
        except Exception as e:
            logger.error(f"清空日志时发生错误: {e}")
            return False
    
    def _deploy_with_retry(self, max_retries: int = 3) -> bool:
        """
        带重试机制的部署方法
        
        Args:
            max_retries: 最大重试次数
            
        Returns:
            bool: 部署是否成功
        """
        for attempt in range(max_retries):
            logger.info(f"尝试部署服务... (第 {attempt + 1}/{max_retries} 次)")
            
            if self.deploy(detached=True):
                return True
            else:
                if attempt < max_retries - 1:
                    logger.warning(f"部署失败，等待 10 秒后重试...")
                    time.sleep(10)
                else:
                    logger.error("所有部署尝试都失败了")
        
        return False
    
    def _remove_data_volumes(self) -> bool:
        """删除Docker数据卷"""
        try:
            # 切换到项目目录
            old_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            try:
                # 删除volumes
                result = subprocess.run(
                    ["docker-compose", "-f", str(self.docker_compose_file), "down", "-v"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    logger.info("Docker数据卷已删除")
                    
                    # 额外删除可能存在的命名卷
                    self._remove_named_volumes()
                    return True
                else:
                    logger.warning(f"删除数据卷警告: {result.stderr}")
                    return False
                    
            finally:
                os.chdir(old_cwd)
                
        except Exception as e:
            logger.error(f"删除数据卷时发生错误: {e}")
            return False
    
    def _remove_named_volumes(self):
        """删除可能存在的命名数据卷"""
        try:
            # 获取项目名称（通常是目录名）
            project_name = self.project_root.name.lower()
            
            # 可能的卷名称
            volume_names = [
                f"{project_name}_loki-data",
                f"{project_name}_grafana-data",
                "loki-data",
                "grafana-data"
            ]
            
            for volume_name in volume_names:
                try:
                    result = subprocess.run(
                        ["docker", "volume", "rm", volume_name],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"已删除数据卷: {volume_name}")
                    
                except Exception:
                    # 卷可能不存在，忽略错误
                    pass
                    
        except Exception as e:
            logger.warning(f"删除命名卷时发生错误: {e}")
    
    def _clean_local_data(self):
        """清理本地数据目录"""
        try:
            # 可能的本地数据目录
            data_dirs = [
                self.project_root / "data",
                self.project_root / "loki-data", 
                self.project_root / "grafana-data",
                self.project_root / "volumes"
            ]
            
            for data_dir in data_dirs:
                if data_dir.exists():
                    logger.info(f"清理本地数据目录: {data_dir}")
                    try:
                        # 删除目录内容但保留目录
                        for item in data_dir.iterdir():
                            if item.is_file():
                                item.unlink()
                            elif item.is_dir():
                                shutil.rmtree(item)
                        logger.info(f"已清理: {data_dir}")
                    except PermissionError:
                        logger.warning(f"权限不足，无法清理: {data_dir}")
                    except Exception as e:
                        logger.warning(f"清理目录时发生错误: {data_dir}, {e}")
                        
        except Exception as e:
            logger.warning(f"清理本地数据时发生错误: {e}")
    
    def get_log_stats(self) -> Dict[str, Any]:
        """
        获取Loki日志统计信息
        
        Returns:
            Dict[str, Any]: 日志统计信息
        """
        try:
            # 查询总日志数量（近24小时）
            query_url = f"{self.loki_url}/loki/api/v1/query"
            
            # 使用简单的查询获取日志统计
            params = {
                "query": 'sum(count_over_time({job!=""}[24h]))',
                "time": str(int(time.time()))
            }
            
            response = requests.get(query_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = data.get('data', {}).get('result', [])
                
                total_logs = 0
                if result and len(result) > 0:
                    value = result[0].get('value', [])
                    if len(value) > 1:
                        total_logs = int(float(value[1]))
                
                # 获取标签信息
                labels_url = f"{self.loki_url}/loki/api/v1/labels"
                labels_response = requests.get(labels_url, timeout=10)
                labels_count = 0
                
                if labels_response.status_code == 200:
                    labels_data = labels_response.json()
                    labels_count = len(labels_data.get('data', []))
                
                return {
                    "total_logs_24h": total_logs,
                    "labels_count": labels_count,
                    "status": "healthy" if self._check_loki_health() else "unhealthy",
                    "loki_url": self.loki_url
                }
            else:
                return {"error": f"查询失败: HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": f"获取统计信息失败: {e}"}
    
    def check_health(self) -> bool:
        """
        检查服务健康状态
        
        Returns:
            bool: 所有服务是否健康
        """
        logger.info("检查服务健康状态...")
        
        # 检查Loki健康状态
        loki_healthy = self._check_loki_health()
        
        # 检查Grafana健康状态  
        grafana_healthy = self._check_grafana_health()
        
        return loki_healthy and grafana_healthy
    
    def _check_loki_health(self) -> bool:
        """检查Loki健康状态"""
        try:
            health_url = f"{self.loki_url}/ready"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                logger.success("Loki服务健康状态正常")
                return True
            else:
                logger.error(f"Loki服务健康检查失败: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Loki健康检查请求失败: {e}")
            return False
    
    def _check_grafana_health(self) -> bool:
        """检查Grafana健康状态"""
        try:
            health_url = f"{self.grafana_url}/api/health"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                logger.success("Grafana服务健康状态正常")
                return True
            else:
                logger.error(f"Grafana服务健康检查失败: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Grafana健康检查请求失败: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取服务状态信息
        
        Returns:
            Dict[str, Any]: 服务状态信息
        """
        try:
            # 切换到项目目录
            old_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            try:
                result = subprocess.run(
                    ["docker-compose", "-f", str(self.docker_compose_file), "ps"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                status_info = {
                    "docker_compose_output": result.stdout,
                    "loki_url": self.loki_url,
                    "grafana_url": self.grafana_url,
                    "loki_healthy": self._check_loki_health(),
                    "grafana_healthy": self._check_grafana_health()
                }
                
                # 添加日志统计信息
                status_info.update(self.get_log_stats())
                
                return status_info
                
            finally:
                os.chdir(old_cwd)
                
        except Exception as e:
            logger.error(f"获取状态信息时发生错误: {e}")
            return {"error": str(e)}
    
    def show_logs(self, service: Optional[str] = None, follow: bool = False) -> bool:
        """
        显示服务日志
        
        Args:
            service: 指定服务名称（loki或grafana），为None时显示所有服务日志
            follow: 是否持续跟踪日志
            
        Returns:
            bool: 命令执行是否成功
        """
        try:
            cmd = ["docker-compose", "-f", str(self.docker_compose_file), "logs"]
            
            if follow:
                cmd.append("-f")
            
            if service:
                cmd.append(service)
            
            # 切换到项目目录
            old_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            try:
                # 直接运行命令，不捕获输出（让日志直接显示在终端）
                subprocess.run(cmd)
                return True
                
            finally:
                os.chdir(old_cwd)
                
        except Exception as e:
            logger.error(f"显示日志时发生错误: {e}")
            return False
    
    def get_service_urls(self) -> Dict[str, str]:
        """
        获取服务访问地址
        
        Returns:
            Dict[str, str]: 服务地址字典
        """
        return {
            "loki": self.loki_url,
            "grafana": self.grafana_url,
            "loki_push_api": f"{self.loki_url}/loki/api/v1/push",
            "grafana_login": "admin/admin123"
        }
    
    def _check_health_with_retry(self, max_retries: int = 6, wait_between: int = 10) -> bool:
        """
        带重试机制的健康检查
        
        Args:
            max_retries: 最大重试次数
            wait_between: 重试间隔时间（秒）
            
        Returns:
            bool: 健康检查是否成功
        """
        for attempt in range(max_retries):
            logger.info(f"健康检查尝试 {attempt + 1}/{max_retries}...")
            
            if self.check_health():
                return True
            
            if attempt < max_retries - 1:
                logger.info(f"健康检查失败，等待 {wait_between} 秒后重试...")
                time.sleep(wait_between)
            else:
                logger.error("所有健康检查尝试都失败了")
        
        return False 