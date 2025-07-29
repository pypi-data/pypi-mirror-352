"""
模型服务器管理模块

包含：
1. 本地模型服务器启动/停止
2. 服务器状态监控
3. 进程管理
"""

import subprocess
import time
import os
import psutil
import requests
import threading
import signal

class ModelServer:
    """
    模型服务器管理类
    
    功能：
    - 启动本地模型服务器
    - 停止服务器及其子进程
    - 监控服务器状态
    - 管理服务器日志
    """
    
    def __init__(self, koboldcpp_path="koboldcpp.exe", default_model="Qwen3-0.6B-Q8_0.gguf", default_port=5001):
        self.koboldcpp_path = koboldcpp_path
        self.default_model = default_model
        self.default_port = default_port
        self.process = None
        self.log_lines = []
        self.status = "stopped"
        self.retry_count = 0
    
    def start_server(self, model_path=None, port=None):
        """
        启动模型服务器
        
        参数:
        model_path - 模型文件路径
        port - 服务器端口
        
        返回:
        bool - 是否成功启动
        """
        if self.is_running():
            return False
        
        model_path = model_path or self.default_model
        port = port or self.default_port
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        
        command = [
            self.koboldcpp_path,
            "--model", model_path,
            "--port", str(port),
        ]
        
        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.status = "starting"
            self.retry_count = 0
            self.log_lines = []
            
            # 启动日志监控线程
            threading.Thread(
                target=self._monitor_output,
                daemon=True
            ).start()
            
            # 启动状态检查
            threading.Thread(
                target=self._check_server_status,
                args=(port,),
                daemon=True
            ).start()
            
            return True
        except Exception as e:
            self.status = "error"
            self.log_lines.append(f"启动服务器失败: {str(e)}")
            return False
    
    def stop_server(self):
        """停止服务器"""
        if not self.is_running():
            return False
        
        try:
            pid = self.process.pid
            self.process.terminate()
            
            # 等待5秒
            for _ in range(5):
                if self.process.poll() is not None:
                    break
                time.sleep(1)
            
            # 如果仍未停止，强制终止
            if self.process.poll() is None:
                self.process.kill()
            
            # 终止子进程
            self._kill_child_processes(pid)
            
            self.status = "stopped"
            self.log_lines.append("服务器已停止")
            return True
        except Exception as e:
            self.log_lines.append(f"停止服务器失败: {str(e)}")
            return False
    
    def is_running(self):
        """检查服务器是否在运行"""
        return self.process and self.process.poll() is None
    
    def get_logs(self, max_lines=100):
        """获取服务器日志"""
        if len(self.log_lines) > max_lines:
            return self.log_lines[-max_lines:]
        return self.log_lines
    
    def _monitor_output(self):
        """监控服务器输出"""
        while self.is_running():
            try:
                line = self.process.stdout.readline()
                if line:
                    self.log_lines.append(line.strip())
            except:
                break
    
    def _check_server_status(self, port):
        """检查服务器状态"""
        while self.status == "starting" and self.retry_count < 10:
            self.retry_count += 1
            try:
                response = requests.get(f"http://localhost:{port}/api/extra/version", timeout=1)
                if response.status_code == 200:
                    self.status = "running"
                    self.log_lines.append("服务器启动成功")
                    return
            except:
                pass
            time.sleep(2)
        
        if self.status == "starting":
            self.status = "error"
            self.log_lines.append(f"服务器启动失败，请检查端口 {port} 是否被占用")
    
    def _kill_child_processes(self, parent_pid):
        """递归终止所有子进程"""
        try:
            parent = psutil.Process(parent_pid)
            children = parent.children(recursive=True)
            
            # 先终止所有子进程
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass
            
            # 等待子进程终止
            gone, still_alive = psutil.wait_procs(children, timeout=5)
            
            # 强制终止仍在运行的子进程
            for child in still_alive:
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
        except psutil.NoSuchProcess:
            pass
        except Exception as e:
            self.log_lines.append(f"终止子进程时出错: {str(e)}")