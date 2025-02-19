import hashlib
import logging
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
from watchdog.utils.dirsnapshot import DirectorySnapshot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Snapshoter:
    """快照管理类，用于保存和加载目录快照"""
    def __init__(self, snapshot_dir: str = "./core/file_management/.snapshots",
                 interval: timedelta = timedelta(minutes=15),
                 max_snapshots: int = 24):
        self.snapshot_dir = Path(snapshot_dir)
        self.interval = interval
        self.max_snapshots = max_snapshots
        self.last_update: Dict[str, datetime] = {}

        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def _get_snapshot_dir(self, path: str) -> Path:
        """获取或创建特定路径的快照存储目录"""
        path = str(Path(path).resolve())
        path_hash = hashlib.md5(path.encode()).hexdigest()
        snapshot_dir = self.snapshot_dir / path_hash
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        # 创建path.info文件记录原始路径
        info_file = snapshot_dir / "path.info"
        if not info_file.exists():
            info_file.write_text(f"Snapshot Path: {path}\nCreated: {datetime.now()}")
        return snapshot_dir

    def _cleanup_old_snapshots(self, snapshot_dir: Path):
        """清理旧的快照文件，确保不超过最大快照数量"""
        snapshots = sorted(snapshot_dir.glob("snapshot_*.pkl"))
        if len(snapshots) > self.max_snapshots:
            for snapshot in snapshots[:len(snapshots) - self.max_snapshots]:
                snapshot.unlink()
                logger.info(f"清理旧快照: {snapshot}")

    def update_snapshot(self, path: str, snapshot: Optional[DirectorySnapshot] = None) -> Optional[Path]:
        """保存目录快照"""
        current_time = datetime.now()
        if not snapshot:
            snapshot = DirectorySnapshot(path)

        snapshot_dir = self._get_snapshot_dir(path)
        snapshot_path = snapshot_dir / f"snapshot_{current_time.strftime('%Y%m%d_%H%M%S')}.pkl"

        try:
            with snapshot_path.open('wb') as f:
                pickle.dump(snapshot, f)
            self.last_update[path] = current_time
            self._cleanup_old_snapshots(snapshot_dir)
            return snapshot_path
        except Exception as e:
            logger.error(f"保存目录快照失败: {path} - {e}")
            return None

    def load_latest_snapshot(self, path: str) -> Optional[DirectorySnapshot]:
        """加载最新的快照"""
        snapshot_dir = self._get_snapshot_dir(path)
        snapshots = sorted(snapshot_dir.glob("snapshot_*.pkl"))
        if not snapshots:
            return None
        snapshot_path = snapshots[-1]
        try:
            with snapshot_path.open('rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"加载目录快照失败：{path} - {e}")
            return None
