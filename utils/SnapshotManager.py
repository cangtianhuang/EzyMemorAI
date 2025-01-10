import hashlib
import os
import pickle
import shutil
from datetime import datetime, timedelta
from typing import Optional, Dict
from watchdog.utils.dirsnapshot import DirectorySnapshot


class SnapshotManager:
    def __init__(self, base_snapshot_dir: str = ".snapshots",
                 save_interval: timedelta = timedelta(minutes=15),
                 max_snapshots: int = 24):
        """
        初始化快照管理器

        Args:
            base_snapshot_dir: 快照文件存储目录
            save_interval: 保存快照的时间间隔
            max_snapshots: 最大保存的快照数量
        """
        self.base_snapshot_dir = base_snapshot_dir
        self.save_interval = save_interval
        self.max_snapshots = max_snapshots

        # 创建快照存储目录
        if not os.path.exists(base_snapshot_dir):
            os.makedirs(base_snapshot_dir)

        # 为每个路径记录最后保存时间
        self.last_save_times: Dict[str, datetime] = {}

    def reset(self):
        """
        重置快照管理器
        """
        self.last_save_times.clear()

        if not os.path.exists(self.base_snapshot_dir):
            os.makedirs(self.base_snapshot_dir)
            return

        while True:
            try:
                shutil.rmtree(self.base_snapshot_dir)
                os.makedirs(self.base_snapshot_dir)
                return
            except OSError as e:
                while True:
                    response = input(
                        f"无法删除或创建目录 {self.base_snapshot_dir}，请确保没有文件被占用：{str(e)}"
                        f"\n请选择操作 ([R]etry/[S]kip/[C]ancel): "
                    ).lower()

                    if response in ['r', 'retry']:
                        break
                    elif response in ['s', 'skip']:
                        return
                    elif response in ['c', 'cancel']:
                        return

    def _get_path_hash(self, aim_path: str) -> str:
        """
        生成路径的唯一标识符

        Args:
            aim_path: 监控的目录路径

        Returns:
            str: 路径的hash值，用作目录名
        """
        return hashlib.md5(aim_path.encode()).hexdigest()[:8]

    def _get_path_snapshot_dir(self, aim_path: str) -> str:
        """
        获取特定路径的快照存储目录

        Args:
            aim_path: 监控的目录路径

        Returns:
            str: 快照存储目录的完整路径
        """
        path_hash = self._get_path_hash(aim_path)
        snapshot_dir = os.path.join(self.base_snapshot_dir, path_hash)
        if not os.path.exists(snapshot_dir):
            os.makedirs(snapshot_dir)
            # 创建path.info文件记录原始路径
            with open(os.path.join(snapshot_dir, "path.info"), "w") as f:
                f.write(f"Original Path: {aim_path}\nCreated: {datetime.now()}")
        return snapshot_dir

    def get_snapshot_path(self, aim_path: str, timestamp: Optional[datetime] = None) -> str:
        """
        获取快照文件路径

        Args:
            aim_path: 监控的目录路径
            timestamp: 快照时间戳

        Returns:
            str: 快照文件的完整路径
        """
        if timestamp is None:
            timestamp = datetime.now()
        snapshot_dir = self._get_path_snapshot_dir(aim_path)
        filename = f"snapshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.pkl"
        return os.path.join(snapshot_dir, filename)

    def save_snapshot(self, aim_path: str, snapshot: DirectorySnapshot, force: bool = False) -> Optional[str]:
        """
        保存目录快照

        Args:
            aim_path: 监控的目录路径
            snapshot: 要保存的DirectorySnapshot对象
            force: 是否强制保存，忽略时间间隔

        Returns:
            Optional[str]: 保存的快照文件路径，如果保存失败则返回None
        """
        current_time = datetime.now()

        # 检查是否需要保存
        if not force and aim_path in self.last_save_times:
            time_elapsed = current_time - self.last_save_times[aim_path]
            if time_elapsed < self.save_interval:
                return None

        # 保存快照
        snapshot_path = self.get_snapshot_path(aim_path, current_time)
        try:
            with open(snapshot_path, 'wb') as f:
                pickle.dump(snapshot, f)

            self.last_save_times[aim_path] = current_time
            self.cleanup_old_snapshots(aim_path)
            return snapshot_path
        except Exception as e:
            print(f"Error saving snapshot for {aim_path}: {str(e)}")
            return None

    def load_latest_snapshot(self, aim_path: str) -> Optional[DirectorySnapshot]:
        """
        加载最新的快照

        Args:
            aim_path: 监控的目录路径

        Returns:
            Optional[DirectorySnapshot]: 最新的快照对象，如果没有则返回None
        """
        snapshot_files = self._get_snapshot_files(aim_path)
        if not snapshot_files:
            return None

        latest_snapshot_path = snapshot_files[-1]
        try:
            with open(latest_snapshot_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading snapshot for {aim_path}: {str(e)}")
            return None

    def cleanup_old_snapshots(self, aim_path: str):
        """
        清理特定路径的旧快照文件

        Args:
            aim_path: 监控的目录路径
        """
        snapshot_files = self._get_snapshot_files(aim_path)
        if len(snapshot_files) > self.max_snapshots:
            files_to_delete = snapshot_files[:-self.max_snapshots]
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Warning: Failed to delete old snapshot {file_path}: {str(e)}")

    def get_snapshot(self, aim_path: str, timestamp_str: str) -> Optional[DirectorySnapshot]:
        """
        获取指定时间戳的快照

        Args:
            aim_path: 监控的目录路径
            timestamp_str: 快照时间戳字符串，格式为'YYYYMMDD_HHMMSS'

        Returns:
            Optional[DirectorySnapshot]: 找到的快照对象，如果不存在返回None
        """
        snapshot_dir = self._get_path_snapshot_dir(aim_path)
        snapshot_path = os.path.join(snapshot_dir, f"snapshot_{timestamp_str}.pkl")
        if not os.path.exists(snapshot_path):
            print(f"Snapshot not found for {aim_path}: {timestamp_str}")
            return None

        try:
            with open(snapshot_path, 'rb') as f:
                return pickle.load(f)
        except (pickle.UnpicklingError, EOFError, AttributeError) as e:
            print(f"Error loading snapshot {timestamp_str} for {aim_path}: {e}")
            return None

    def delete_snapshot(self, aim_path: str, timestamp_str: str) -> bool:
        """
        删除指定时间戳的快照

        Args:
            aim_path: 监控的目录路径
            timestamp_str: 快照时间戳字符串，格式为'YYYYMMDD_HHMMSS'

        Returns:
            bool: 是否成功删除
        """
        snapshot_dir = self._get_path_snapshot_dir(aim_path)
        snapshot_path = os.path.join(snapshot_dir, f"snapshot_{timestamp_str}.pkl")
        if not os.path.exists(snapshot_path):
            print(f"Snapshot not found for {aim_path}: {timestamp_str}")
            return False

        try:
            os.remove(snapshot_path)
            return True
        except OSError as e:
            print(f"Error deleting snapshot {timestamp_str} for {aim_path}: {e}")
            return False

    def get_snapshot_info(self) -> dict:
        """
        获取所有快照的基本信息

        Returns:
            dict: 以原始路径为key的字典,value包含该路径的所有快照信息列表
        """
        all_info = {}

        for path_hash in os.listdir(self.base_snapshot_dir):
            path_dir = os.path.join(self.base_snapshot_dir, path_hash)
            if not os.path.isdir(path_dir):
                continue

            # 读取path.info获取原始路径信息
            path_info_file = os.path.join(path_dir, "path.info")
            try:
                with open(path_info_file, "r") as f:
                    info_content = f.read()
                    original_path = info_content.split("Original Path: ")[1].split("\n")[0]
                    created_time = datetime.strptime(
                        info_content.split("Created: ")[1],
                        "%Y-%m-%d %H:%M:%S.%f"
                    )
            except (FileNotFoundError, IndexError, ValueError) as e:
                print(f"Error reading path info for {path_hash}: {e}")
                continue

            # 获取该路径下所有快照信息
            snapshot_info = []
            for filepath in self._get_snapshot_files(original_path):
                filename = os.path.basename(filepath)
                try:
                    timestamp = datetime.strptime(
                        filename[9:-4],
                        '%Y%m%d_%H%M%S'
                    )
                    file_size = os.path.getsize(filepath)
                    snapshot_info.append({
                        'timestamp': timestamp,
                        'file_size': file_size,
                        'path': filepath
                    })
                except (ValueError, OSError) as e:
                    print(f"Error getting info for snapshot {filename}: {e}")
                    continue

            all_info[original_path] = {
                "created_time": created_time,
                "snapshots": sorted(snapshot_info, key=lambda x: x['timestamp'])
            }

        return all_info

    def _get_snapshot_files(self, aim_path: str) -> list:
        """
        获取特定路径的所有快照文件并按时间排序

        Args:
            aim_path: 监控的目录路径

        Returns:
            list: 排序后的快照文件路径列表
        """
        snapshot_dir = self._get_path_snapshot_dir(aim_path)
        files = [os.path.join(snapshot_dir, f) for f in os.listdir(snapshot_dir)
                 if f.startswith('snapshot_') and f.endswith('.pkl')]
        return sorted(files)
