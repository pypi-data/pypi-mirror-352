import os
import sys
import hashlib
import logging
from logging.handlers import RotatingFileHandler
import paramiko
import threading
from tqdm import tqdm
import concurrent
from concurrent.futures import ThreadPoolExecutor, as_completed
from scp import SCPClient, SCPException
import re
from mdbq.config import config
import time
import datetime
import argparse
import ast
from functools import wraps
import queue
from typing import (
    Any, Optional, Union, Dict, List, Tuple, Set, Callable,
    TypeVar, Generic, Iterable, Iterator, cast,
    BinaryIO, TextIO, Pattern, Match, NoReturn
)

__version__ = '1.2.6'

PathLike = Union[str, os.PathLike]
SSHClient = paramiko.SSHClient
SCPClientT = SCPClient
Logger = logging.Logger
Handler = logging.Handler
FileHandler = logging.FileHandler
RotatingFileHandlerT = logging.handlers.RotatingFileHandler
ThreadPoolExecutorT = ThreadPoolExecutor
Future = concurrent.futures.Future
PatternT = Pattern[str]
MatchT = Match[str]
Queue = queue.Queue
DictStrAny = Dict[str, Any]
ListStr = List[str]
TupleStr = Tuple[str, ...]
SetStr = Set[str]
CallableT = TypeVar('CallableT', bound=Callable[..., Any])

# 读取配置文件
dir_path: str = os.path.expanduser("~")
content: Dict[str, Any] = config.read_config(file_path=os.path.join(dir_path, 'spd.txt'))


def set_log() -> Logger:
    """配置日志系统"""
    # 日志级别映射
    level_dict: Dict[str, int] = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    # 从配置中获取日志级别，默认为CRITICAL
    log_level_name: str = content.get('scp_log_level', 'CRITICAL').upper()
    log_level: int = level_dict.get(log_level_name, level_dict['CRITICAL'])

    # 配置日志文件路径
    log_file_name: str = content.get('scp_log_file', 'spd.txt')
    log_file: str = os.path.join(dir_path, 'logfile', log_file_name)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)  # 创建日志目录

    # 设置文件处理器，支持日志轮转
    file_handler: RotatingFileHandlerT = RotatingFileHandler(
        filename=log_file,
        maxBytes=3 * 1024 * 1024,  # 单个日志文件最大3MB
        backupCount=10,  # 保留10个备份文件
        encoding='utf-8'
    )
    stream_handler: Handler = logging.StreamHandler()  # 控制台输出处理器
    formatter: logging.Formatter = logging.Formatter(
        fmt='[%(asctime)s] %(message)s',  # 日志格式
        datefmt='%Y-%m-%d %H:%M:%S'  # 日期格式
    )
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # 设置处理器日志级别
    file_handler.setLevel(log_level)
    stream_handler.setLevel(log_level)

    # 配置根日志记录器
    logger: Logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(log_level)

    # 设置paramiko的日志级别为WARNING，减少不必要的日志输出
    ssh_logger: Logger = logging.getLogger("paramiko.transport")
    ssh_logger.setLevel(logging.WARNING)
    return logger


logger: Logger = set_log()  # 初始化日志记录器


def time_cost(func: CallableT) -> CallableT:
    """计算函数执行时间的装饰器"""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        def format_duration(seconds: float) -> str:
            """格式化时间显示"""
            hours: int = int(seconds // 3600)
            remainder: float = seconds % 3600
            minutes: int = int(remainder // 60)
            seconds_remaining: float = remainder % 60
            seconds_remaining = round(seconds_remaining, 2)

            parts: List[str] = []
            if hours > 0:
                parts.append(f"{hours}小时")
            if minutes > 0 or (hours > 0 and seconds_remaining > 0):
                parts.append(f"{minutes}分")
            if seconds_remaining < 10 and (hours == 0 and minutes == 0):
                parts.append(f"{seconds_remaining}秒")
            elif seconds_remaining < 10 and (hours != 0 or minutes != 0):
                parts.append(f"0{int(seconds_remaining)}秒")
            else:
                parts.append(f"{int(seconds_remaining)}秒")
            return ''.join(parts)

        before: float = time.time()  # 记录开始时间
        result: str = func(*args, **kwargs)
        after: float = time.time()  # 记录结束时间
        duration: float = after - before
        formatted_time: str = format_duration(duration)
        logger.info(f'[计时] {formatted_time}')
        return result

    return cast(CallableT, wrapper)


class SCPCloud:
    """SCP文件传输工具类，支持上传和下载文件/文件夹"""

    def __init__(
            self,
            host: str,
            port: int,
            user: str,
            password: str,
            max_workers: int = 5,
            log_file: str = 'cloud.log'
    ) -> None:
        """初始化SCP客户端"""
        self.host: str = host  # 主机地址
        self.port: int = port  # 端口号
        self.user: str = user  # 用户名
        self.password: str = password  # 密码
        self.max_workers: int = max_workers  # 最大工作线程数
        self.ssh_lock: threading.Lock = threading.Lock()  # SSH连接锁
        self.pbar_lock: threading.Lock = threading.Lock()  # 进度条锁
        self.pbars: Dict[str, tqdm] = {}  # 存储进度条对象
        self.skip: List[str] = ['.DS_Store']  # 默认跳过的文件
        self.next_bar_pos: int = 0  # 下一个进度条位置
        self.position_map: Dict[str, int] = {}  # 进度条位置映射
        self.download_skip: List[str] = []  # 下载跳过的文件
        self.path_sep: str = '/'  # 路径分隔符
        self._connection_pool: Queue[SSHClient] = queue.Queue(maxsize=max_workers)  # SSH连接池
        self._remote_file_cache: Dict[str, str] = {}  # 远程文件MD5缓存
        self._cache_lock: threading.Lock = threading.Lock()  # 缓存锁
        self._log_buffer: List[str] = []  # 日志缓冲区
        self._last_flush: float = time.time()  # 上次刷新日志时间
        self._connection_timeout: int = 30  # 连接超时时间
        self._command_timeout: int = 60  # 命令执行超时时间
        self._max_retry: int = 3  # 最大重试次数

    def _is_connection_healthy(self, ssh: SSHClient) -> bool:
        """检查SSH连接是否健康"""
        try:
            stdin, stdout, stderr = ssh.exec_command("echo 'health_check'", timeout=self._command_timeout)
            return stdout.read().decode().strip() == 'health_check'
        except Exception:
            return False

    def _flush_logs(self) -> None:
        """刷新日志缓冲区"""
        if time.time() - self._last_flush > 1 and self._log_buffer:
            for msg in self._log_buffer:
                logger.info(msg)
            self._log_buffer.clear()
            self._last_flush = time.time()

    def _format_log(self, msg: str, operation: Optional[str]) -> str:
        """格式化日志信息，添加操作类型并限制长度"""
        operation = operation.lower()
        # 操作类型映射
        operation_map = {
            'upload': '上传',
            'download': '下载',
            'mkdir': '创建目录',
            'skip': '跳过',
            'info': 'INFO',
            'verify': 'VERIFY',  # MD5不匹配不属于异常
            'error': '异常',
        }
        op_display = operation_map.get(operation)

        # 限制日志长度
        max_length = 500
        if len(msg) > max_length:
            msg = f"{msg[:max_length]}...[截断，共{len(msg)}字符]"

        if op_display:
            return f"[{op_display}] {msg}"
        else:
            return f'{msg}'

    def _log_info(self, msg: str, operation: Optional[str] = 'info') -> None:
        """记录日志信息"""
        msg = msg or ""
        formatted_msg = self._format_log(msg, operation)
        self._log_buffer.append(formatted_msg)
        self._flush_logs()

    def _get_ssh_connection(self) -> SSHClient:
        """从连接池获取或创建SSH连接"""
        while True:
            try:
                ssh: SSHClient = self._connection_pool.get_nowait()
                if self._is_connection_healthy(ssh):
                    return ssh
                else:
                    ssh.close()
            except queue.Empty:
                return self._create_ssh_connection()

    def _return_ssh_connection(self, ssh: Optional[SSHClient]) -> None:
        """归还SSH连接到连接池"""
        if ssh is None:
            return

        try:
            if ssh.get_transport() is None or not ssh.get_transport().is_active():
                ssh.close()
                return

            if self._connection_pool.qsize() < self.max_workers:
                if self._is_connection_healthy(ssh):
                    self._connection_pool.put(ssh)
                else:
                    ssh.close()
            else:
                ssh.close()
        except Exception:
            if ssh:
                ssh.close()

    def _normalize_path(self, path: Optional[str], is_remote: bool = False) -> Optional[str]:
        """规范化路径"""
        if not path:
            return path
        path = path.replace('\\', '/').rstrip('/')
        if not is_remote:
            path = os.path.normpath(path)
        return path

    def _create_ssh_connection(self) -> SSHClient:
        """创建新的SSH连接"""
        for attempt in range(self._max_retry):
            try:
                ssh: SSHClient = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.user,
                    password=self.password,
                    look_for_keys=False,
                    timeout=self._connection_timeout,
                    banner_timeout=30
                )
                return ssh
            except Exception as e:
                if attempt == self._max_retry - 1:
                    raise
                time.sleep(1)
        raise Exception("Failed to create SSH connection after retries")

    def upload(self, local_path: str, remote_path: str) -> None:
        """上传文件或文件夹"""
        ssh: SSHClient = self._get_ssh_connection()
        try:
            # 处理主目录路径
            local_path = self.check_home_path(local_path, is_remote=False, ssh=ssh)
            remote_path = self.check_home_path(remote_path, is_remote=True, ssh=ssh)

            if os.path.isfile(local_path):  # 上传单个文件
                scp: SCPClientT = SCPClient(ssh.get_transport(), socket_timeout=60, progress=self._progress_bar)
                self._upload_file(local_path=local_path, remote_path=remote_path, ssh=ssh, scp=scp)
            elif os.path.isdir(local_path):  # 上传文件夹
                self._upload_folder(local_dir=local_path, remote_dir=remote_path)
            else:
                self._log_info(f'不存在的本地路径: "{local_path}", 请检查路径, 建议输入完整绝对路径', 'error')
        finally:
            self._return_ssh_connection(ssh)

    def _upload_folder(self, local_dir: str, remote_dir: str) -> None:
        """上传文件夹"""
        remote_dir = remote_dir.rstrip('/') + '/'
        local_dir = local_dir.rstrip('/') + '/'

        create_dir_list: List[str] = []  # 需要创建的远程目录列表
        upload_list: List[Dict[str, str]] = []  # 需要上传的文件列表

        # 遍历本地目录结构
        for root, _, files in os.walk(local_dir):
            ls_dir: str = re.sub(f'^{local_dir}', '', root)
            create_dir_list.append(os.path.join(remote_dir, ls_dir))
            for file in files:
                local_file: str = os.path.join(root, file)
                if self._skip_file(file):  # 跳过指定文件
                    continue
                ls_file: str = re.sub(f'^{local_dir}', '', f'{local_file}')
                remote_file: str = os.path.join(remote_dir, ls_file)
                upload_list.append({local_file: remote_file})

        self._log_info(f'目录预检(不存在将自动创建)\n{'\n'.join(create_dir_list)}')
        self._batch_mkdir_remote(create_dir_list)  # 批量创建远程目录

        # 使用线程池并发上传文件
        with ThreadPoolExecutor(self.max_workers) as pool:
            futures: List[Future[None]] = [pool.submit(self._upload_file_thread, item) for item in upload_list]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self._log_info(f"上传失败: {e}", 'error')

    def _batch_mkdir_remote(self, paths: List[str]) -> None:
        """批量创建远程目录"""
        if not paths:
            return
        ssh: SSHClient = self._get_ssh_connection()
        try:
            commands: str = ';'.join(f'mkdir -p "{path}"' for path in paths)
            ssh.exec_command(commands)
        finally:
            self._return_ssh_connection(ssh)

    def _upload_file_thread(self, _args: Dict[str, str]) -> None:
        """上传文件的线程函数"""
        for local_path, remote_path in _args.items():
            ssh: SSHClient = self._get_ssh_connection()
            scp: SCPClientT = SCPClient(ssh.get_transport(), socket_timeout=60, progress=self._progress_bar)
            try:
                self._upload_file(local_path, remote_path, ssh, scp)
            finally:
                scp.close()
                self._return_ssh_connection(ssh)

    def _upload_file(
            self,
            local_path: str,
            remote_path: str,
            ssh: SSHClient,
            scp: SCPClientT
    ) -> None:
        """上传单个文件"""
        local_path = self._normalize_path(local_path)
        remote_path = self._normalize_path(remote_path, is_remote=True)

        # 如果远程路径是目录，则在路径后添加文件名
        if self._remote_is_dir(ssh, remote_path):
            remote_path = f"{remote_path}/{os.path.basename(local_path)}"

        remote_path = remote_path.rstrip('/')
        remote_dir: str = os.path.dirname(remote_path)
        self._mkdir_remote(remote_dir)  # 创建远程目录

        # 检查是否需要上传(文件不存在或MD5不同)
        if not self._should_upload(ssh, local_path, remote_path):
            self._log_info(f"File Exists -> {remote_path}")
            return

        self._log_info(f'{local_path} -> {remote_path}', 'upload')
        scp.put(local_path, remote_path, preserve_times=True)  # 上传文件并保留时间属性

        # 校验文件完整性
        if not self._verify_download(ssh=ssh, local_path=local_path, remote_path=remote_path):
            self._log_info(f"MD5校验失败 -> lc: {local_path} -> rm: {remote_path}", 'verify')

    def _should_upload(self, ssh: SSHClient, local_path: str, remote_path: str) -> bool:
        """检查是否需要上传文件"""
        remote_path = self._normalize_path(remote_path, is_remote=True)

        if not self._remote_is_file(ssh, remote_path):  # 远程文件不存在
            return True

        if not self._remote_exists(ssh, remote_path):  # 远程路径不存在
            return True

        # 比较本地和远程文件的MD5
        local_md5: Optional[str] = self._get_local_md5(local_path)
        remote_md5: Optional[str] = self._get_remote_md5(ssh, remote_path)
        return local_md5 != remote_md5

    def _get_local_md5(self, path: str) -> Optional[str]:
        """计算本地文件的MD5值"""
        if not os.path.isfile(path):
            return None
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _get_remote_md5(self, ssh: SSHClient, path: str) -> Optional[str]:
        """获取远程文件的MD5值"""
        with self._cache_lock:
            if path in self._remote_file_cache:  # 检查缓存
                return self._remote_file_cache[path]

        path = self._normalize_path(path, is_remote=True)
        # 使用openssl或md5sum计算MD5
        cmd: str = f' (test -f "{path}" && (openssl md5 -r "{path}" 2>/dev/null || md5sum "{path}")) || echo "NOT_FILE"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output: str = stdout.read().decode().strip()

        if output == "NOT_FILE" or not output:
            return None

        result: str = output.split()[0]
        with self._cache_lock:
            self._remote_file_cache[path] = result  # 缓存结果
        return result

    def _remote_exists(self, ssh: SSHClient, path: str) -> bool:
        """检查远程路径是否存在"""
        stdin, stdout, stderr = ssh.exec_command(f'[ -e "{path}" ] && echo exists')
        return stdout.read().decode().strip() == 'exists'

    def _mkdir_remote(self, path: str) -> None:
        """创建远程目录"""
        ssh: SSHClient = self._get_ssh_connection()
        try:
            ssh.exec_command(f'mkdir -p "{path}"')
        finally:
            self._return_ssh_connection(ssh)

    def _skip_file(self, file_path: str) -> bool:
        """检查是否需要跳过文件"""
        if self.skip:
            for skip in self.skip:
                if skip in file_path:
                    return True
        return False

    def _progress_bar(self, filename: bytes, size: int, sent: int) -> None:
        """上传进度条回调函数"""
        try:
            filename_str: str = filename.decode('utf-8', errors='replace')
        except Exception:
            filename_str = str(filename)

        with self.pbar_lock:  # 获取资源锁
            if filename_str not in self.pbars:
                display_size: int = max(size, 1)
                new_pbar: tqdm = tqdm(
                    total=display_size,
                    unit='B',
                    unit_scale=True,
                    desc=f'上传 {os.path.basename(filename_str)}',
                    position=self.next_bar_pos,  # 固定位置分配
                    leave=True,  # 完成后保留进度条显示
                    miniters=1,
                    dynamic_ncols=True,
                    lock_args=None  # 使用全局锁
                )
                self.pbars[filename_str] = new_pbar
                self.position_map[filename_str] = self.next_bar_pos
                self.next_bar_pos += 1  # 位置计数器递增
                if size == 0:  # 空文件特殊处理
                    with self.pbar_lock:  # 将回收操作纳入锁保护范围
                        new_pbar.update(1)
                        new_pbar.close()
                        del self.pbars[filename_str]
                        self.next_bar_pos -= 1  # 回收位置
                        return
            # 获取目标进度条及位置信息
            target_pbar: Optional[tqdm] = self.pbars.get(filename_str)
            if not target_pbar:
                return
            # target_pbar.clear()  # 先清除旧内容
            current: int = target_pbar.n
            safe_total: int = target_pbar.total
            increment: int = max(0, min(sent, safe_total) - current)
            if increment > 0:
                target_pbar.update(increment)
                target_pbar.refresh()  # 立即刷新显示
            if target_pbar.n >= target_pbar.total and filename_str in self.pbars:
                target_pbar.close()
                del self.pbars[filename_str]
                self.next_bar_pos -= 1  # 回收位置计数器

    def download(self, remote_path: str, local_path: str) -> None:
        """下载文件或文件夹"""
        ssh: SSHClient = self._get_ssh_connection()
        try:
            # 处理主目录路径
            local_path = self.check_home_path(local_path, is_remote=False, ssh=ssh)
            remote_path = self.check_home_path(remote_path, is_remote=True, ssh=ssh)

            if self._remote_is_dir(ssh, remote_path):  # 下载文件夹
                self._download_folder(remote_dir=remote_path, local_dir=local_path, ssh=ssh)
            elif self._remote_is_file(ssh, remote_path):  # 下载单个文件
                self._download_file(remote_path=remote_path, local_path=local_path, ssh=ssh)
            else:
                self._log_info(f'不存在的远程路径: "{remote_path}", 请检查路径, 建议输入完整绝对路径', 'error')
        finally:
            self._return_ssh_connection(ssh)

    def _remote_is_file(self, ssh: SSHClient, path: str) -> bool:
        """检查远程路径是否为文件"""
        path = self._normalize_path(path, is_remote=True)
        stdin, stdout, stderr = ssh.exec_command(f'[ -f "{path}" ] && echo file')
        return stdout.read().decode().strip() == 'file'

    def _remote_is_dir(self, ssh: SSHClient, path: str) -> bool:
        """检查远程路径是否为目录"""
        path = path.rstrip('/')
        stdin, stdout, stderr = ssh.exec_command(f'[ -d "{path}" ] && echo directory')
        return stdout.read().decode().strip() == 'directory'

    def _download_folder(self, remote_dir: str, local_dir: str, ssh: SSHClient) -> None:
        """下载文件夹"""
        remote_dir = remote_dir.rstrip('/') + '/'
        local_dir = local_dir.rstrip('/') + '/'

        # 获取远程目录结构
        file_tree: Dict[str, List[str]] = self._get_remote_tree(ssh, remote_dir)

        # 创建本地目录结构
        dirs_to_create: List[str] = [os.path.join(local_dir, d.replace(remote_dir, '', 1)) for d in file_tree['dirs']]
        for d in dirs_to_create:
            os.makedirs(d, exist_ok=True)

        # 准备下载文件列表
        download_list: List[Dict[str, str]] = []
        for remote_file in file_tree['files']:
            local_file: str = os.path.join(local_dir, remote_file.replace(remote_dir, '', 1))
            if self._skip_file(remote_file):  # 跳过指定文件
                self._log_info(f'跳过文件: {remote_file}', 'skip')
                continue
            download_list.append({remote_file: local_file})

        # 使用线程池并发下载文件
        with ThreadPoolExecutor(self.max_workers) as pool:
            futures: List[Future[None]] = [pool.submit(self._download_file_thread, item) for item in download_list]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self._log_info(f"下载失败: {e}", 'error')

    def _get_remote_tree(self, ssh: SSHClient, root_dir: str) -> Dict[str, List[str]]:
        """获取远程目录结构"""
        tree: Dict[str, List[str]] = {'dirs': [], 'files': []}
        stdin, stdout, stderr = ssh.exec_command(f'find "{root_dir}" -type d')
        for line in stdout:
            tree['dirs'].append(line.strip())

        stdin, stdout, stderr = ssh.exec_command(f'find "{root_dir}" -type f')
        for line in stdout:
            tree['files'].append(line.strip())
        return tree

    def _download_file_thread(self, _args: Dict[str, str]) -> None:
        """下载文件的线程函数"""
        for rm_path, lc_path in _args.items():
            ssh: SSHClient = self._get_ssh_connection()
            scp: SCPClientT = SCPClient(ssh.get_transport(), socket_timeout=60, progress=self._download_progress)
            try:
                self._download_file(rm_path, lc_path, ssh, scp)
            finally:
                scp.close()
                self._return_ssh_connection(ssh)

    def _download_file(
            self,
            remote_path: str,
            local_path: str,
            ssh: SSHClient,
            scp: Optional[SCPClientT] = None
    ) -> None:
        """下载单个文件"""
        remote_path = self._normalize_path(remote_path, is_remote=True)
        local_path = self._normalize_path(local_path)

        # 如果本地路径是目录，则在路径后添加文件名
        if os.path.isdir(local_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))

        if scp is None:
            scp = SCPClient(ssh.get_transport(), socket_timeout=60, progress=self._download_progress)

        # 检查是否需要下载(文件不存在或MD5不同)
        if not self._should_download(ssh, remote_path, local_path):
            self._log_info(f"File Exists -> {local_path}")
            return

        if os.path.isdir(local_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))

        try:
            self._log_info(f'{remote_path} -> {local_path}', 'download')
            scp.get(remote_path, local_path=local_path, preserve_times=True)  # 下载文件并保留时间属性
        except Exception as e:
            self._log_info(f"Error details: {e.__class__.__name__}, {e.args}", 'error')

        # 校验文件完整性
        if not self._verify_download(ssh=ssh, remote_path=remote_path, local_path=local_path):
            self._log_info(f"MD5校验失败 -> rm: {remote_path} -> lc: {local_path}", 'verify')

    def _should_download(self, ssh: SSHClient, remote_path: str, local_path: str) -> bool:
        """检查是否需要下载文件"""
        if not os.path.exists(local_path):  # 本地文件不存在
            return True
        remote_md5: Optional[str] = self._get_remote_md5(ssh, remote_path)
        local_md5: Optional[str] = self._get_local_md5(local_path)
        return remote_md5 != local_md5  # 比较MD5值

    def _verify_download(self, ssh: SSHClient, remote_path: str, local_path: str) -> bool:
        """验证下载文件的完整性"""
        return self._get_remote_md5(ssh, remote_path) == self._get_local_md5(local_path)

    def _download_progress(self, filename: bytes, size: int, sent: int) -> None:
        """下载进度回调函数"""
        try:
            filename_str: str = filename.decode('utf-8', errors='replace')
        except Exception:
            filename_str = str(filename)
        with self.pbar_lock:
            if filename_str not in self.pbars:
                new_pbar: tqdm = tqdm(
                    total=size,
                    unit='B',
                    unit_scale=True,
                    desc=f'下载 {os.path.basename(filename_str)}',
                    position=self.next_bar_pos,
                    leave=True,
                    dynamic_ncols=True
                )
                self.pbars[filename_str] = new_pbar
                self.position_map[filename_str] = self.next_bar_pos
                self.next_bar_pos += 1

            target_pbar: Optional[tqdm] = self.pbars.get(filename_str)
            if not target_pbar:
                return

            current: int = target_pbar.n
            increment: int = max(0, min(sent, size) - current)
            if increment > 0:
                target_pbar.update(increment)

            if target_pbar.n >= target_pbar.total and filename_str in self.pbars:
                target_pbar.close()
                del self.pbars[filename_str]
                self.next_bar_pos -= 1

    def check_home_path(self, path: Optional[str], is_remote: bool = False, ssh: Optional[SSHClient] = None) -> \
    Optional[str]:
        """处理主目录路径(~)"""
        if not path:
            return None
        path = self._normalize_path(path, is_remote=is_remote)
        if str(path).startswith('~'):
            if is_remote:
                if not ssh:
                    self._log_info(f'ssh 不能为 none', 'error')
                    return None
                stdin, stdout, stderr = ssh.exec_command("echo $HOME")
                home_path: str = stdout.read().decode().strip()
            else:
                home_path = os.path.expanduser("~")
            return path.replace('~', home_path, 1)
        else:
            return path

    def _cleanup_connections(self) -> None:
        """清理所有SSH连接"""
        while not self._connection_pool.empty():
            try:
                ssh: SSHClient = self._connection_pool.get_nowait()
                ssh.close()
            except Exception:
                pass

    def __del__(self) -> None:
        """析构函数，清理连接"""
        self._cleanup_connections()


@time_cost
def main(debug: bool = False) -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='上传下载')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}', help='')
    parser.add_argument('-u', '--upload', nargs=2, help='')
    parser.add_argument('-d', '--download', nargs=2, help='')
    args: argparse.Namespace = parser.parse_args()

    # 初始化SCP客户端
    cloud: SCPCloud = SCPCloud(
        host=content['scp_host'],
        port=int(content['scp_port']),
        user=content['scp_user'],
        password=content['scp_password'],
        max_workers=int(content['scp_max_workers']),
        log_file=content['scp_log_file']
    )
    cloud.skip = ast.literal_eval(content['scp_skip'])

    if debug:
        args.download = ['logfile', '~/downloads/']

    # 处理上传/下载命令
    if args.upload:
        local_path: str = args.upload[0]
        remoto_path: str = args.upload[1]
        cloud.upload(local_path=local_path, remote_path=remoto_path)
    elif args.download:
        remoto_path: str = args.download[0]
        local_path: str = args.download[1]
        cloud.download(remote_path=remoto_path, local_path=local_path)


if __name__ == "__main__":
    main(debug=False)
