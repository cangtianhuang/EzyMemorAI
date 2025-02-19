import logging
import threading
from typing import Optional

from watchdog.events import FileSystemEventHandler

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core.file_management.processor import FileProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WatcherHandler(FileSystemEventHandler):
    """文件监控的回调处理类，与文件解析、向量数据库、文档数据库交互"""
    def __init__(self, path: str, processor: 'FileProcessor', debounce_seconds: float = 5):
        super().__init__()
        logger.info(f"初始化Watcher: {path}")
        self.path = path
        self.processor = processor
        self.debounce_seconds = debounce_seconds
        self.timer: Optional[threading.Timer] = None
        self.snapshot = self.processor.load_snapshot(path)
        self._process_changes()

    def on_any_event(self, event):
        """处理文件系统事件"""
        if self.processor.is_ignore(event.src_path):
            logger.info(f"忽略文件: {event.src_path}")
            return
        self._start_debounce_timer()

    def _start_debounce_timer(self):
        """启动防抖计时器"""
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.debounce_seconds, self._process_changes)
        self.timer.start()

    def _process_changes(self):
        """处理文件变化"""
        self.snapshot = self.processor.process_snapshot_diff(self.path, self.snapshot)
        self.timer = None

    def dispose(self):
        """释放资源"""
        if self.timer:
            self.timer.cancel()
        self.timer = None