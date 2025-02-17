import hashlib
import pickle
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
from watchdog.utils.dirsnapshot import DirectorySnapshot

class Snapshoter:
    def __init__(self, snapshot_dir: str = ".snapshots",
                 interval: timedelta = timedelta(minutes=15),
                 max_snapshots: int = 24):
        """
        初始化快照管理器

        Args:
            snapshot_dir: 快照文件存储目录
            interval: 保存快照的时间间隔
            max_snapshots: 最大保存的快照数量
        """
        self.snapshot_dir = Path(snapshot_dir)
        self.interval = interval
        self.max_snapshots = max_snapshots
        self.last_update: Dict[str, datetime] = {}

        self.snapshot_dir.mkdir(parents=True, exist_ok=True)


    def reset(self):
        """重置快照管理器"""
        self.last_update.clear()
        if self.snapshot_dir.exists():
            try:
                shutil.rmtree(self.snapshot_dir)
            except OSError as e:
                print(f"无法删除目录: {self.snapshot_dir} - {e}")
                return
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def _create_snapshot_dir(self, target_path: str) -> Path:
        """创建特定路径的快照存储目录"""
        path_hash = hashlib.md5(target_path.encode()).hexdigest()[:8]
        snapshot_dir = self.snapshot_dir / path_hash
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        # 创建path.info文件记录原始路径
        info_file = snapshot_dir / "path.info"
        if not info_file.exists():
            info_file.write_text(f"Snapshot Path: {target_path}\nCreated: {datetime.now()}")
        return snapshot_dir

    def update_snapshot(self, target_path: str, snapshot: Optional[DirectorySnapshot]) -> Optional[Path]:
        """保存目录快照"""
        current_time = datetime.now()
        if snapshot is None:
            snapshot = DirectorySnapshot(target_path)
        snapshot_path = self._create_snapshot_dir(target_path) / f"snapshot_{current_time.strftime('%Y%m%d%_H%M%S')}.pkl"
        try:
            with snapshot_path.open('wb') as f:
                pickle.dump(snapshot, f)
            self.last_update[target_path] = current_time
            return snapshot_path
        except Exception as e:
            print(f"保存目录快照失败: {target_path} - {e}")
            return None

    def load_snapshot(self, target_path: str) -> Optional[DirectorySnapshot]:
        """加载最新的快照"""
        path_hash = hashlib.md5(target_path.encode()).hexdigest()[:8]
        snapshot_dir = self.snapshot_dir / path_hash
        if not snapshot_dir.exists():
            return None
        snapshot_path = sorted(snapshot_dir.glob("snapshot_*.pkl"))[-1]
        try:
            with snapshot_path.open('rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"加载目录快照失败：{target_path} - {e}")
            return None
