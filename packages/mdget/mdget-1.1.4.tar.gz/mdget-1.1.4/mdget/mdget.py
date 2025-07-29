import os
import sys
import hashlib
import logging
from logging.handlers import RotatingFileHandler
import paramiko
import threading
from tqdm import tqdm
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

__version__ = '1.1.4'

dir_path = os.path.expanduser("~")
content = config.read_config(file_path=os.path.join(dir_path, 'spd.txt'))


def set_log():
    level_dict = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    log_level_name = content.get('scp_log_level', 'CRITICAL').upper()
    log_level = level_dict.get(log_level_name, level_dict['CRITICAL'])

    log_file_name = content.get('scp_log_file', 'spd.txt')
    log_file = os.path.join(dir_path, 'logfile', log_file_name)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=3 * 1024 * 1024,
        backupCount=10,
        encoding='utf-8'
    )
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt='[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    file_handler.setLevel(log_level)
    stream_handler.setLevel(log_level)

    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(log_level)

    ssh_logger = logging.getLogger("paramiko.transport")
    ssh_logger.setLevel(logging.WARNING)
    return logger


logger = set_log()


def time_cost(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        def format_duration(seconds):
            hours = int(seconds // 3600)
            remainder = seconds % 3600
            minutes = int(remainder // 60)
            seconds_remaining = remainder % 60
            seconds_remaining = round(seconds_remaining, 2)

            parts = []
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

        before = time.time()
        result = func(*args, **kwargs)
        after = time.time()
        duration = after - before
        formatted_time = format_duration(duration)
        logger.info(f'用时：{formatted_time}')
        return result

    return wrapper


class SCPCloud:
    def __init__(self, host, port, user, password, max_workers=5, log_file='cloud.log'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.max_workers = max_workers
        self.ssh_lock = threading.Lock()
        self.pbar_lock = threading.Lock()
        self.pbars = {}
        self.skip = ['.DS_Store']
        self.next_bar_pos = 0
        self.position_map = {}
        self.download_skip = []
        self.path_sep = '/'
        self._connection_pool = queue.Queue(maxsize=max_workers)
        self._remote_file_cache = {}
        self._cache_lock = threading.Lock()
        self._log_buffer = []
        self._last_flush = time.time()
        self._connection_timeout = 30
        self._command_timeout = 60
        self._max_retry = 3

    def _is_connection_healthy(self, ssh):
        try:
            stdin, stdout, stderr = ssh.exec_command("echo 'health_check'",
                                                     timeout=self._command_timeout)
            return stdout.read().decode().strip() == 'health_check'
        except:
            return False

    def _flush_logs(self):
        if time.time() - self._last_flush > 1 and self._log_buffer:
            logger.info('\n'.join(self._log_buffer))
            self._log_buffer.clear()
            self._last_flush = time.time()

    def _log_info(self, msg):
        self._log_buffer.append(msg)
        self._flush_logs()

    def _get_ssh_connection(self):
        while True:
            try:
                ssh = self._connection_pool.get_nowait()
                if self._is_connection_healthy(ssh):
                    return ssh
                else:
                    ssh.close()
            except queue.Empty:
                return self._create_ssh_connection()

    def _return_ssh_connection(self, ssh):
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
        except:
            if ssh:
                ssh.close()

    def _normalize_path(self, path, is_remote=False):
        if not path:
            return path
        path = path.replace('\\', '/').rstrip('/')
        if not is_remote:
            path = os.path.normpath(path)
        return path

    def _create_ssh_connection(self):
        for attempt in range(self._max_retry):
            try:
                ssh = paramiko.SSHClient()
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

    def upload(self, local_path, remote_path):
        ssh = self._get_ssh_connection()
        try:
            local_path = self.check_home_path(local_path, is_remote=False, ssh=ssh)
            remote_path = self.check_home_path(remote_path, is_remote=True, ssh=ssh)
            if os.path.isfile(local_path):
                scp = SCPClient(ssh.get_transport(), socket_timeout=60, progress=self._progress_bar)
                self._upload_file(local_path=local_path, remote_path=remote_path, ssh=ssh, scp=scp)
            elif os.path.isdir(local_path):
                self._upload_folder(local_dir=local_path, remote_dir=remote_path)
            else:
                self._log_info(f'不存在的本地路径: "{local_path}", 请检查路径, 建议输入完整绝对路径')
        finally:
            self._return_ssh_connection(ssh)

    def _upload_folder(self, local_dir, remote_dir):
        remote_dir = remote_dir.rstrip('/') + '/'
        local_dir = local_dir.rstrip('/') + '/'

        create_dir_list = []
        upload_list = []
        for root, _, files in os.walk(local_dir):
            ls_dir = re.sub(f'^{local_dir}', '', root)
            create_dir_list.append(os.path.join(remote_dir, ls_dir))
            for file in files:
                local_file = os.path.join(root, file)
                if self._skip_file(file):
                    continue
                ls_file = re.sub(f'^{local_dir}', '', f'{local_file}')
                remote_file = os.path.join(remote_dir, ls_file)
                upload_list.append({local_file: remote_file})

        self._log_info(f'预检目录(不存在将创建) {create_dir_list}')
        self._batch_mkdir_remote(create_dir_list)

        with ThreadPoolExecutor(self.max_workers) as pool:
            futures = [pool.submit(self._upload_file_thread, item) for item in upload_list]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self._log_info(f"上传失败: {e}")

    def _batch_mkdir_remote(self, paths):
        if not paths:
            return
        ssh = self._get_ssh_connection()
        try:
            commands = ';'.join(f'mkdir -p "{path}"' for path in paths)
            ssh.exec_command(commands)
        finally:
            self._return_ssh_connection(ssh)

    def _upload_file_thread(self, _args):
        for local_path, remote_path in _args.items():
            ssh = self._get_ssh_connection()
            scp = SCPClient(ssh.get_transport(), socket_timeout=60, progress=self._progress_bar)
            try:
                self._upload_file(local_path, remote_path, ssh, scp)
            finally:
                scp.close()
                self._return_ssh_connection(ssh)

    def _upload_file(self, local_path, remote_path, ssh, scp):
        local_path = self._normalize_path(local_path)
        remote_path = self._normalize_path(remote_path, is_remote=True)

        if self._remote_is_dir(ssh, remote_path):
            remote_path = f"{remote_path}/{os.path.basename(local_path)}"

        remote_path = remote_path.rstrip('/')
        remote_dir = os.path.dirname(remote_path)
        self._mkdir_remote(remote_dir)

        if not self._should_upload(ssh, local_path, remote_path):
            self._log_info(f"文件已存在rm {remote_path}")
            return

        self._log_info(f'{local_path} -> {remote_path}')
        scp.put(local_path, remote_path, preserve_times=True)
        if not self._verify_download(ssh=ssh, local_path=local_path, remote_path=remote_path):
            self._log_info(f"MD5校验失败 -> lc: {local_path} -> rm: {remote_path}")

    def _should_upload(self, ssh, local_path, remote_path):
        remote_path = self._normalize_path(remote_path, is_remote=True)

        if not self._remote_is_file(ssh, remote_path):
            return True

        if not self._remote_exists(ssh, remote_path):
            return True

        local_md5 = self._get_local_md5(local_path)
        remote_md5 = self._get_remote_md5(ssh, remote_path)
        return local_md5 != remote_md5

    def _get_local_md5(self, path):
        if not os.path.isfile(path):
            return None
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _get_remote_md5(self, ssh, path):
        with self._cache_lock:
            if path in self._remote_file_cache:
                return self._remote_file_cache[path]

        path = self._normalize_path(path, is_remote=True)
        cmd = f' (test -f "{path}" && (openssl md5 -r "{path}" 2>/dev/null || md5sum "{path}")) || echo "NOT_FILE"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode().strip()

        if output == "NOT_FILE" or not output:
            return None

        result = output.split()[0]
        with self._cache_lock:
            self._remote_file_cache[path] = result
        return result

    def _remote_exists(self, ssh, path):
        stdin, stdout, stderr = ssh.exec_command(f'[ -e "{path}" ] && echo exists')
        return stdout.read().decode().strip() == 'exists'

    def _mkdir_remote(self, path):
        ssh = self._get_ssh_connection()
        try:
            ssh.exec_command(f'mkdir -p "{path}"')
        finally:
            self._return_ssh_connection(ssh)

    def _skip_file(self, file_path):
        if self.skip:
            for skip in self.skip:
                if skip in file_path:
                    return True
        return False

    def _progress_bar(self, filename, size, sent):
        try:
            filename_str = filename.decode('utf-8', errors='replace')
        except Exception:
            filename_str = filename

        if not hasattr(threading.current_thread(), '_last_update'):
            threading.current_thread()._last_update = 0

        now = time.time()
        if now - threading.current_thread()._last_update < 0.1:
            return

        threading.current_thread()._last_update = now

        with self.pbar_lock:
            if filename_str not in self.pbars:
                display_size = max(size, 1)
                new_pbar = tqdm(
                    total=display_size,
                    unit='B',
                    unit_scale=True,
                    desc=f'上传 {os.path.basename(filename_str)}',
                    position=self.next_bar_pos,
                    leave=True,
                    miniters=1,
                    dynamic_ncols=True,
                    lock_args=None
                )
                self.pbars[filename_str] = new_pbar
                self.position_map[filename_str] = self.next_bar_pos
                self.next_bar_pos += 1
                if size == 0:
                    with self.pbar_lock:
                        new_pbar.update(1)
                        new_pbar.close()
                        del self.pbars[filename_str]
                        self.next_bar_pos -= 1
                        return

            target_pbar = self.pbars.get(filename_str)
            if not target_pbar:
                return

            current = target_pbar.n
            safe_total = target_pbar.total
            increment = max(0, min(sent, safe_total) - current)
            if increment > 0:
                target_pbar.update(increment)
                target_pbar.refresh()

            if target_pbar.n >= target_pbar.total and filename_str in self.pbars:
                target_pbar.close()
                del self.pbars[filename_str]
                self.next_bar_pos -= 1

    def download(self, remote_path, local_path):
        ssh = self._get_ssh_connection()
        try:
            local_path = self.check_home_path(local_path, is_remote=False, ssh=ssh)
            remote_path = self.check_home_path(remote_path, is_remote=True, ssh=ssh)
            if self._remote_is_dir(ssh, remote_path):
                self._download_folder(remote_dir=remote_path, local_dir=local_path, ssh=ssh)
            elif self._remote_is_file(ssh, remote_path):
                self._download_file(remote_path=remote_path, local_path=local_path, ssh=ssh)
            else:
                self._log_info(f'不存在的远程路径: "{remote_path}", 请检查路径, 建议输入完整绝对路径')
        finally:
            self._return_ssh_connection(ssh)

    def _remote_is_file(self, ssh, path):
        path = self._normalize_path(path, is_remote=True)
        stdin, stdout, stderr = ssh.exec_command(f'[ -f "{path}" ] && echo file')
        return stdout.read().decode().strip() == 'file'

    def _remote_is_dir(self, ssh, path):
        path = path.rstrip('/')
        stdin, stdout, stderr = ssh.exec_command(f'[ -d "{path}" ] && echo directory')
        return stdout.read().decode().strip() == 'directory'

    def _download_folder(self, remote_dir, local_dir, ssh):
        remote_dir = remote_dir.rstrip('/') + '/'
        local_dir = local_dir.rstrip('/') + '/'

        file_tree = self._get_remote_tree(ssh, remote_dir)

        dirs_to_create = [os.path.join(local_dir, d.replace(remote_dir, '', 1)) for d in file_tree['dirs']]
        for d in dirs_to_create:
            os.makedirs(d, exist_ok=True)

        download_list = []
        for remote_file in file_tree['files']:
            local_file = os.path.join(local_dir, remote_file.replace(remote_dir, '', 1))
            if self._skip_file(remote_file):
                self._log_info(f'跳过文件: {remote_file}')
                continue
            download_list.append({remote_file: local_file})

        with ThreadPoolExecutor(self.max_workers) as pool:
            futures = [pool.submit(self._download_file_thread, item) for item in download_list]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self._log_info(f"下载失败: {e}")

    def _get_remote_tree(self, ssh, root_dir):
        tree = {'dirs': [], 'files': []}
        stdin, stdout, stderr = ssh.exec_command(f'find "{root_dir}" -type d')
        for line in stdout:
            tree['dirs'].append(line.strip())

        stdin, stdout, stderr = ssh.exec_command(f'find "{root_dir}" -type f')
        for line in stdout:
            tree['files'].append(line.strip())
        return tree

    def _download_file_thread(self, _args):
        for rm_path, lc_path in _args.items():
            ssh = self._get_ssh_connection()
            scp = SCPClient(ssh.get_transport(), socket_timeout=60, progress=self._download_progress)
            try:
                self._download_file(rm_path, lc_path, ssh, scp)
            finally:
                scp.close()
                self._return_ssh_connection(ssh)

    def _download_file(self, remote_path, local_path, ssh, scp=None):
        remote_path = self._normalize_path(remote_path, is_remote=True)
        local_path = self._normalize_path(local_path)

        if os.path.isdir(local_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))

        if scp is None:
            scp = SCPClient(ssh.get_transport(), socket_timeout=60, progress=self._download_progress)

        if not self._should_download(ssh, remote_path, local_path):
            self._log_info(f"文件已存在lc {local_path}")
            return

        if os.path.isdir(local_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))

        try:
            self._log_info(f'{remote_path} -> {local_path}')
            scp.get(remote_path, local_path=local_path, preserve_times=True)
        except Exception as e:
            self._log_info(f"Error details: {e.__class__.__name__}, {e.args}")

        if not self._verify_download(ssh=ssh, remote_path=remote_path, local_path=local_path):
            self._log_info(f"MD5校验失败 -> rm: {remote_path} -> lc: {local_path}")

    def _should_download(self, ssh, remote_path, local_path):
        if not os.path.exists(local_path):
            return True
        remote_md5 = self._get_remote_md5(ssh, remote_path)
        local_md5 = self._get_local_md5(local_path)
        return remote_md5 != local_md5

    def _verify_download(self, ssh, remote_path, local_path):
        return self._get_remote_md5(ssh, remote_path) == self._get_local_md5(local_path)

    def _download_progress(self, filename, size, sent):
        try:
            filename_str = filename.decode('utf-8', errors='replace')
        except Exception:
            filename_str = filename

        if not hasattr(threading.current_thread(), '_last_update'):
            threading.current_thread()._last_update = 0

        now = time.time()
        if now - threading.current_thread()._last_update < 0.1:
            return

        threading.current_thread()._last_update = now

        with self.pbar_lock:
            if filename_str not in self.pbars:
                new_pbar = tqdm(
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

            target_pbar = self.pbars.get(filename_str)
            if not target_pbar:
                return

            current = target_pbar.n
            increment = max(0, min(sent, size) - current)
            if increment > 0:
                target_pbar.update(increment)

            if target_pbar.n >= target_pbar.total and filename_str in self.pbars:
                target_pbar.close()
                del self.pbars[filename_str]
                self.next_bar_pos -= 1

    def check_home_path(self, path, is_remote=False, ssh=None):
        if not path:
            return
        path = self._normalize_path(path, is_remote=is_remote)
        if str(path).startswith('~'):
            if is_remote:
                if not ssh:
                    self._log_info(f'ssh 不能为 none')
                    return
                stdin, stdout, stderr = ssh.exec_command("echo $HOME")
                home_path = stdout.read().decode().strip()
            else:
                home_path = os.path.expanduser("~")
            return path.replace('~', home_path, 1)
        else:
            return path

    def _cleanup_connections(self):
        """清理所有连接"""
        while not self._connection_pool.empty():
            try:
                ssh = self._connection_pool.get_nowait()
                ssh.close()
            except:
                pass

    def __del__(self):
        self._cleanup_connections()

@time_cost
def main(debug=False):
    parser = argparse.ArgumentParser(description='上传下载')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}', help='')
    parser.add_argument('-u', '--upload', nargs=2, help='')
    parser.add_argument('-d', '--download', nargs=2, help='')
    args = parser.parse_args()

    cloud = SCPCloud(
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

    if args.upload:
        local_path, remoto_path = args.upload[0], args.upload[1]
        cloud.upload(local_path=local_path, remote_path=remoto_path)
    elif args.download:
        remoto_path, local_path = args.download[0], args.download[1]
        cloud.download(remote_path=remoto_path, local_path=local_path)


if __name__ == "__main__":
    main(debug=False)